import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from presentation.server.main_server import main

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
