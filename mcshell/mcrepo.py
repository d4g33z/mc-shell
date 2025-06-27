from mcshell.constants import *

from abc import ABC, abstractmethod


class PowerRepository(ABC):
    """
    Abstract base class defining the interface for storing and retrieving powers.
    This decouples the main application from the specific database implementation.
    """

    @abstractmethod
    def save_power(self, power_data: Dict[str, Any]) -> str:
        """
        Saves a new power or updates an existing one for a specific player.
        Args:
            power_data: A dictionary containing all data for the power.
        Returns:
            The unique ID of the saved power.
        """
        pass

    @abstractmethod
    def list_powers(self) -> List[Dict[str, Any]]:
        """
        Lists summary data for all saved powers for a player.
        Should return lightweight data (id, name, description, category),
        not the full blockly_json or python_code.

        Args:
        Returns:
            A list of dictionaries, each a power summary.
        """
        pass

    @abstractmethod
    def list_full_powers(self) -> List[Dict[str, Any]]:
        """
        Lists all data for all saved powers for a player.

        Args:
        Returns:
            A list of dictionaries, each the full power data.
        """
        pass

    @abstractmethod
    def get_full_power(self, power_id: str) -> Optional[Dict[str, Any]]:
        """
        Loads the full data for a single power, including the code.

        Args:
            power_id: The unique identifier for the power.
        Returns:
            A dictionary containing all data for the power, or None if not found.
        """
        pass

    @abstractmethod
    def delete_power(self, power_id: str) -> bool:
        """
        Deletes a specific power for a player.

        Args:
            power_id: The unique identifier for the power.
        Returns:
            True on success, False on failure.
        """
        pass

class JsonFileRepository(PowerRepository):
    def __init__(self, player_name: str):
        # self.storage_path = pathlib.Path(storage_path)
        # self.storage_path.mkdir(exist_ok=True)
        self.player_name = player_name
        MC_POWER_LIBRARY_DIR.mkdir(exist_ok=True)

    def _get_player_data(self) -> Dict[str, Any]:
        """Helper to load a player's entire power data file."""
        player_file = MC_POWER_LIBRARY_DIR.joinpath(f"{self.player_name}.json")
        if player_file.exists():
            with open(player_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {} # Return empty dict if file is corrupt or empty
        return {}

    def _save_player_data(self,data: Dict[str, Any]):
        """Helper to save a player's entire power data file."""
        player_file = MC_POWER_LIBRARY_DIR.joinpath(f"{self.player_name}.json")
        with open(player_file, 'w') as f:
            json.dump(data, f, indent=4)

    def save_power(self, power_data: Dict[str, Any]) -> str:
        all_powers = self._get_player_data()

        # Assign a new ID if one doesn't exist
        power_id = power_data.get("power_id") or str(uuid.uuid4())
        power_data["power_id"] = power_id

        all_powers[power_id] = power_data
        self._save_player_data(all_powers)
        return power_id

    def list_full_powers(self) -> List[Dict[str, Any]]:
        """
        Lists ALL data for all saved powers for the configured player.
        This is the comprehensive version for the control UI's JSON model.
        """
        all_powers_dict = self._get_player_data()
        # Return a list of the complete power data objects
        return list(all_powers_dict.values())

    def list_powers(self) -> List[Dict[str, Any]]:
        all_powers = self._get_player_data()
        # Return only a summary, not the heavy code fields
        summary_list = []
        for power_id, power_data in all_powers.items():
            summary_list.append({
                "power_id": power_id,
                "name": power_data.get("name", "Unnamed Power"),
                "description": power_data.get("description", ""),
                "category": power_data.get("category", "General")
            })
        return summary_list

    def get_full_power(self, power_id: str) -> Optional[Dict[str, Any]]:
        all_powers = self._get_player_data()
        return all_powers.get(power_id)

    def delete_power(self, power_id: str) -> bool:
        all_powers = self._get_player_data()
        if power_id in all_powers:
            del all_powers[power_id]
            self._save_player_data(all_powers)
            return True
        return False