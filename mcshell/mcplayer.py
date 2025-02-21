from mcshell.constants import *
from mcshell.mcclient import MCClient

class MCPlayer(MCClient):
    def __init__(self,name):
        super().__init__(**SERVER_DATA)
        self.name = name
        self.state = {}

    def get_data(self,data_path):
        _args = ['get','entity',f'@p[name={self.name}]',data_path]
        return self.data(*_args)

    def build(self):
        for _data_path in DATA_PATHS:
            _data = self.get_data(_data_path)
            self.state[_data_path] = _data
        _recipe_book_data = {}
        for _data_path in RECIPE_BOOK_DATA_PATHS:
            _data = self.get_data(f"recipeBook.{_data_path}")
            _recipe_book_data[_data_path] = _data
        self.state['recipeBook'] = _recipe_book_data

    # broken due to truncated server responses
    async def get_data_async(self,data_path):
        _args = f"entity @p[name={self.name}] {data_path}".split()
        await self.data_async(data_path,self.state,'get',*_args)

    async def build_player_data_async(self):
        for _data_path in DATA_PATHS:
            await self.get_data_async(_data_path)
        for _data_path in RECIPE_BOOK_DATA_PATHS:
            _data = await self.get_data_async(f"recipeBook.{_data_path}")

    def build_async(self):
        asyncio.run(self.build_player_data_async())

def test_async_data_size(print_values=False):
    async def _test_data_size(print_values):
        _player = MCPlayer('Om5mO')
        for _data_path in DATA_PATHS:
            try:
                _data = await _player.get_data_async(_data_path)
                if print_values:
                    print('-' * 20)
                    print(_data_path)
                    print(_data)
            except:
                print(f"{_data_path} is too long")
                continue

        for _data_path in RECIPE_BOOK_DATA_PATHS:
            try:
                _data = await _player.get_data_async(f"recipeBook.{_data_path}")
                if print_values:
                    print('-' * 20)
                    print(_data_path)
                    print(_data)
            except:
                print(f"{_data_path} is too long")
                continue

    asyncio.run(_test_data_size(print_values))

if __name__ == "__main__":
    test_async_data_size()
