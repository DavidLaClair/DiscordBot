class Media:
    def __init__(self, media_type, category_name):
        self.media_type = media_type
        self.category_name = category_name
        self.category_id = 0
        self.channels = {}
        self.roles = {}

        self.approver_role_name = ""

    def set_category_id(self, id):
        print("We are setting the category id for '{media_type}' to '{id}'".format(media_type=self.media_type, id=id))
        self.category_id = id

    def get_channels(self, guild):
        print("Getting all channels under '{guild_name}-{cat_name}'.".format(guild_name=guild.name, cat_name=self.category_name))

        if self.category_id == 0:
            print("ERROR: The category ID has not been set for {role_type}!")
            return
        
        for channel in guild.channels:
            if channel.category_id == self.category_id:
                self.channels[channel.name] = channel
        
        print("Channels for '{guild_name}-{cat_name}' have been updated to the following:\n{channels}".format(guild_name=guild.name, cat_name=self.category_name, channels=self.channels))

    def get_channel_list(self):
        val = ""

        for key in self.channels:
            val += key + "\n"
        
        return val
    
    def get_role(self, media_name):
        print("Attempting to find a matching role for '{role_type}-{media_name}'".format(role_type=self.media_type, media_name=media_name))

        role = None

        if media_name in self.roles:
            role = self.roles[media_name]
            print("Found a matching role '{role}'".format(role=role))
        else:
            print("No matching role found.")

        return role

    def get_roles(self, guild):
        print("Getting all roles under '{guild_name}-{cat_name}'.".format(guild_name=guild.name, cat_name=self.media_type))

        prefix = self.media_type + "-"
        prefix_len = len(prefix)

        for role in guild.roles:
            if role.name.startswith(prefix):
                media_name = role.name[prefix_len:]
                self.roles[media_name] = role
        
        print("We have finished getting the roles under '{guild_name}-{cat_name}'.\n{roles}".format(guild_name=guild.name, cat_name=self.media_type,roles=self.roles))
    
    def create_role(self, guild, media_name):
        print("Request to create role for '{guild_name}-{media_type}-{media_name}".format(guild_name=guild.name, media_type=self.media_type, media_name=media_name))

        role_name = "{media_type}-{media_name}".format(media_type=self.media_type, media_name=media_name)

        #Create the role in the guild
        new_role = guild.create_role(name=role_name)

        #Add the new role to our DB
        self.roles[media_name] = new_role

        print("Created new role:\n{role}".format(role=new_role))
        return new_role
    
    def create_missing_roles(self, guild):
        print("Request to create missing roles for '{guild_name}-{media_type}'".format(guild_name=guild.name, media_type=self.media_type))
        
        for media_name in self.channels:
            #Check if the channel name has a role
            if media_name not in self.roles:
                print("We found a missing role! We are going to create a role! '{guild_name}-{media_type}-{media_name}'".format(guild_name=guild.name, media_type=self.media_type, media_name=media_name))

                new_role = self.create_role(guild, media_name)

                #Set Permissions on role
                self.channels[media_name].set_permissions(new_role, read_messages=True, send_messages=True, read_message_history=True)

    async def join_role(self, member, role):
        print("We are adding {member} to '{role}'.".format(member=member, role=role))

        await member.add_roles(role)
        print("Added {member} to '{role}'".format(member=member.name, role=role))
    
    async def leave_role(self, member, role):
        print("We are removing {member} from '{role}'.".format(member=member, role=role))

        await member.remove_roles(role)
        print("Removed {member} from '{role}'".format(member=member.name, role=role))