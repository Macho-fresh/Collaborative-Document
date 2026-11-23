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

async def loadbalancer(request):
    server = get_next_server()
    async with aiohttp.ClientSession() as session:
        if server:
            async with session.get(f'http://{server['address']}/') as response:
                print(f'forwarding request to {server['address']}')
                return web.Response(text=f'{await response.text()}', status=response.status)
        return web.Response(text='all servers are unhealthy', status=503)

app = web.Application()
app.add_routes([web.get('/', loadbalancer)])

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)