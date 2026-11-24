import aiohttp
import asyncio
from aiohttp import web

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

async def loadbalancer(request):
    server = get_next_server()
    method = request.method
    headers = request.headers
    print(f'load balancer header: {headers}')
    body = await request.read()

    async with aiohttp.ClientSession() as session:
        if server:
            async with session.request(method, f"http://{server['address']}{request.path_qs}", data=body, headers=headers) as response:
                print(f'forwarding request to {server['address']}')
                outgoing_body = await response.read()
                outgoing_headers = response.headers
                print(f'server header: {outgoing_headers}')

                return web.Response(status=response.status, headers=outgoing_headers, body=outgoing_body)
        return web.Response(text='all servers are unhealthy', status=503)

app = web.Application()
app.add_routes([web.route('*', '/{tail:.*}', loadbalancer)])

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)