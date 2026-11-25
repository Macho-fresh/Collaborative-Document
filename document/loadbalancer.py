import aiohttp
import asyncio
from aiohttp import web
from multidict import CIMultiDict, CIMultiDictProxy

servers = [
    {'address': '127.0.0.1:8001', 'status': 'healthy', 'active_connections': 0, 'requests': 0},
    {'address': '127.0.0.1:8002', 'status': 'healthy', 'active_connections': 0, 'requests': 0}
]


# implement health check loop

index = -1

def get_next_server():
    global index

    index = (index + 1) % len(servers)
    for i in range(len(servers)):
        if servers[index]['status'] == 'healthy':
            return servers[index]
        index = (index + 1) % len(servers)
    return None  

# implement filter_headers() for independent socket handling 
# strip transfer-encoding and connection and its addional headers if any 

def filter_headers(headers, extra_remove=None):
    resp_headers = CIMultiDict() 
    to_remove = {
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailer',
    'transfer-encoding',
    }
    if extra_remove:
        for i in extra_remove:
            to_remove.add(i.lower())

    try:
        if headers['Connection']:
            for l in headers['Connection'].split(','):
                to_remove.add(l.strip().lower())
    except KeyError:
        pass

    for k,v in headers.items():
        if k.lower() not in to_remove:
            resp_headers.add(k, v)
        
    resp_headers = CIMultiDictProxy(resp_headers)
    return resp_headers

async def websocket_handler(request, session, server, headers):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    backend_ws = await session.ws_connect(f'ws://{server["address"]}{request.path_qs}', headers=headers)

    async def to_client():
        async for msg in backend_ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                await ws.close(code=msg.data, message=msg.extra)
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

    async def to_backend():
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await backend_ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await backend_ws.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                await backend_ws.close(code=msg.data, message=msg.extra)
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
            
    tasks = [
    asyncio.create_task(to_client()),
    asyncio.create_task(to_backend()),
    ]

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    await backend_ws.close()
    await ws.close()

    return ws

async def loadbalancer(request):
    server = get_next_server()
    is_ws = request.headers.get('Upgrade', '').lower() == 'websocket'
    headers = request.headers
    ws_headers = CIMultiDict()
    ws_remove = {'host', 'content-lenght'}
    for k,v in headers.items():
        if k.lower() not in ws_remove:
            ws_headers.add(k, v)
    ws_headers = CIMultiDictProxy(ws_headers)
    print(ws_headers)
    if is_ws:
        browser_headers = filter_headers(headers, extra_remove={'host', 'content-length'})
    else:
        browser_headers = filter_headers(headers, extra_remove={'host', 'content-length', 'connection', 'upgrade'})

    body = await request.read()

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(auto_decompress=False, timeout=timeout) as session:
        if is_ws:
            if not server:
                return web.Response(text='all servers are unhealthy', status=503)
            return await websocket_handler(request, session, server, headers=ws_headers)
        else:
            try:
                if server:
                    async with session.request(request.method, f"http://{server['address']}{request.path_qs}", data=body, headers=browser_headers) as response:
                        print(f'forwarding request to {server["address"]}')
                        outgoing_body = await response.read()
                        outgoing_headers = response.headers
                        django_headers = filter_headers(outgoing_headers, extra_remove={'content-length', 'connection', 'upgrade'})
                        
                        return web.Response(status=response.status, headers=django_headers, body=outgoing_body)
                    
                return web.Response(text='all servers are unhealthy', status=503)
            except asyncio.TimeoutError:
                return web.Response(text=f'request timed out', status=504)
            except aiohttp.ClientConnectionError:
                return web.Response(text=f'Bad Gateway', status=502)

app = web.Application()
app.add_routes([web.route('*', '/{tail:.*}', loadbalancer)])

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8000)