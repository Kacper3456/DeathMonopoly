class PlayerManager:
    def __init__(self):
        self.player_data = {
            "name": "You",
            "avatar": "images/game_window/avatar/businessman.png",
            "dialogue": "This is your character. You are the player in this game.",
            "balance": 1000
        }
    
    def get_player_data(self):
        return self.player_data
    
    def set_player_name(self, name):
        self.player_data["name"] = name
    
    def set_player_avatar(self, avatar_path):
        self.player_data["avatar"] = avatar_path
    
    def set_player_dialogue(self, dialogue):
        self.player_data["dialogue"] = dialogue
        
    def set_player_balance(self, balance):
        self.player_data["balance"] = balance
        
    def get_player_balance(self):
        return self.player_data["balance"] 
    
    def update_player_data(self, name=None, avatar=None, dialogue=None):
        if name is not None:
            self.player_data["name"] = name
        if avatar is not None:
            self.player_data["avatar"] = avatar
        if dialogue is not None:
            self.player_data["dialogue"] = dialogue