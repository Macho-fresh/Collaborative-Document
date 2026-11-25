import aiohttp
import asyncio
from aiohttp import web
from multidict import CIMultiDict, CIMultiDictProxy

servers = [
    {'address': '127.0.0.1:8001', 'status': 'healthy', 'active_connections': 0, 'requests': 0},
    {'address': '127.0.0.1:8002', 'status': 'healthy', 'active_connections': 0, 'requests': 0}
]

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
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailer',
    'transfer-encoding',
    'upgrade'
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
    

async def loadbalancer(request):
    server = get_next_server()
    headers = request.headers
    browser_headers = filter_headers(headers, extra_remove={'host', 'content-length'})
    # print(f'browser header: {browser_headers}')
    body = await request.read()

    async with aiohttp.ClientSession(auto_decompress=False) as session:
        if server:
            async with session.request(request.method, f"http://{server['address']}{request.path_qs}", data=body, headers=browser_headers) as response:
                print(f'forwarding request to {server["address"]}')
                outgoing_body = await response.read()
                outgoing_headers = response.headers
                django_headers = filter_headers(outgoing_headers)
                
                return web.Response(status=response.status, headers=django_headers, body=outgoing_body)
        return web.Response(text='all servers are unhealthy', status=503)

app = web.Application()
app.add_routes([web.route('*', '/{tail:.*}', loadbalancer)])

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8000)