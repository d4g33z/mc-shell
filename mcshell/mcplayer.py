from mcshell.mcclient import MCClient
from mcshell.constants import *

# Define a tolerance for floating-point comparisons near zero
DEFAULT_TOLERANCE = 1e-9

class MCPlayer(MCClient):
    def __init__(self,name,host=MC_SERVER_HOST,port=MC_SERVER_PORT,password=None,server_type=MC_SERVER_TYPE,fruit_juice_port=FJ_SERVER_PORT):
        super().__init__(host,port,password,server_type,fruit_juice_port)
        self.name = name
        self.state = {}

    def get_data(self,data_path):
        _args = ['get','entity',f'@p[name={self.name}]',data_path]
        return self.data(*_args)

    def build(self):
        for _data_path in DATA_PATHS:
            if _data_path in FORBIDDEN_DATA_PATHS:
                continue
            _data = self.get_data(_data_path)
            self.state[_data_path] = _data
        _recipe_book_data = {}
        for _data_path in RECIPE_BOOK_DATA_PATHS:
            if _data_path in FORBIDDEN_DATA_PATHS:
                continue
            _data = self.get_data(f"recipeBook.{_data_path}")
            _recipe_book_data[_data_path] = _data
        self.state['recipeBook'] = _recipe_book_data
        return self

    # broken due to truncated server responses
    async def get_data_async(self,data_path):
        _args = f"entity @p[name={self.name}] {data_path}".split()
        await self.data_async(data_path,self.state,'get',*_args)

    async def build_player_data_async(self):
        for _data_path in DATA_PATHS:
            if _data_path in FORBIDDEN_DATA_PATHS:
                continue
            await self.get_data_async(_data_path)
        for _data_path in RECIPE_BOOK_DATA_PATHS:
            if _data_path in FORBIDDEN_DATA_PATHS:
                continue
            _data = await self.get_data_async(f"recipeBook.{_data_path}")

    def build_async(self):
        asyncio.run(self.build_player_data_async())
        return self

    @property
    def pc(self):
        return self.py_client(self.name)

    @property
    def position(self):
        self.build()
        return Vec3(*self.state.get('Pos'))

    @property
    def cardinal_direction(self):
        return self.get_cardial_direction(*self.pc.player.getDirection())

    @property
    def direction(self):
        # note the cast from pyncraft.vec3.Vec3 to mcshell.Vec3.Vec3
        return Vec3(*self.pc.player.getDirection())

    @property
    def here(self):
        return Vec3(*self.get_sword_hit_position())


    def get_sword_hit_position(self):
        '''
            The following sword hits will all be detected:
        	DIAMOND_SWORD,
			GOLDEN_SWORD,
			IRON_SWORD,
			STONE_SWORD,
			WOODEN_SWORD
        '''
        print('Waiting for a sword strike...')

        while True:
            _hits = self.pc.events.pollBlockHits()
            if _hits:
                _hit = _hits[0]
                _v0 = _hit.pos.clone()
                self.pc.events.clearAll()

                # _block = self.pc.getBlock(*_v0)
                #
                # # replace the block
                # self.pc.setBlock(*_v0, _block)

                # _direction, _face = self.get_cardial_direction(*self.pc.player.getDirection())
                # return _hit.pos.clone(), _direction, _face, _block
                return _hit.pos.clone()


    @staticmethod
    def _get_sign(value, tolerance=DEFAULT_TOLERANCE):
      """Determines the sign of a value (-1, 0, or 1) using a tolerance."""
      if value > tolerance:
        return 1
      elif value < -tolerance:
        return -1
      else:
        return 0

    def _get_vector_region(self,vector, tolerance=DEFAULT_TOLERANCE):
      """
      Assigns a 3D vector to one of the 26 tessellation regions surrounding the origin.

      The region is identified by the integer coordinates (I, J, K) of the
      cube in a 3x3x3 grid (relative to the center at (0,0,0)) that the
      vector points towards. I, J, K will be in {-1, 0, 1}.

      Args:
        vector: A list or tuple of 3 floats representing the direction vector (x, y, z).
                It should ideally be a unit vector, but normalization isn't strictly required
                as only the signs matter. Must not be the zero vector.
        tolerance: The tolerance for considering a component to be zero.

      Returns:
        A tuple (I, J, K) representing the region indices. Returns None if the
        input vector is numerically indistinguishable from the zero vector.

      Raises:
        ValueError: If the input is not a 3-component vector.
      """
      if len(vector) != 3:
        raise ValueError("Input must be a 3-component vector.")

      x, y, z = vector

      i = self._get_sign(x, tolerance)
      j = self._get_sign(y, tolerance)
      k = self._get_sign(z, tolerance)

      # Check if the vector was effectively zero
      if i == 0 and j == 0 and k == 0:
        # This should not happen for a unit vector input, but check defensively.
        print("Warning: Input vector is close to zero.")
        return None

      # The tuple (i, j, k) directly represents the target region
      return i, j, k

    def get_cardial_direction(self,i,j,k):
        I, J, K = self._get_vector_region([i, j, k])

        _xdir = ''
        _zdir = ''

        if I > 0:
            _xdir = 'EAST'
        elif I < 0:
            _xdir = 'WEST'

        if K > 0:
            _zdir = 'SOUTH'
        elif K < 0:
            _zdir = 'NORTH'

        if abs(i) > abs(k):
            _direction = i
            _cardinal_direction = _xdir
        else:
            _direction = k
            _cardinal_direction = _zdir

        if J > 0 and  abs(_direction) > math.sqrt(1 / 2):
            _face = 'CEILING'
        elif J < 0 and abs(_direction) < math.sqrt(1 / 2):
            _face = 'FLOOR'
        else:
            _face = 'WALL'

        return _cardinal_direction, _face
