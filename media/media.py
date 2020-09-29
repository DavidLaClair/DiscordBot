import logging

class Media:
    def __init__(self, guild, media_type, category_name):
        self.guild = guild
        self.media_type = media_type
        self.category_name = category_name
        self.category_id = 0
        self.channels = {}
        self.roles = {}

        self.approver_role_name = ""

    def set_category_id(self, id):
        logging.info("'{guild_name}'\t{action}\t{media_type}\t{cat_id}".format(guild_name=self.guild.name, action="set_cat_id", media_type=self.media_type, cat_id=id))
        self.category_id = id

    def get_channels(self):
        logging.info("'{guild_name}'\t{action}\t{media_type}".format(guild_name=self.guild.name, action="get_channels", media_type=self.media_type))

        if self.category_id == 0:
            logging.error("'{guild_name}'\t{action}\t{media_type}\t{result}".format(guild_name=self.guild.name, action="get_channels", media_type=self.media_type, result="Category ID not set"))
            return
        
        for channel in self.guild.channels:
            if channel.category_id == self.category_id:
                self.channels[channel.name] = channel
        
        logging.info("'{guild_name}'\t{action}\t{media_type}\t{result}".format(guild_name=self.guild.name, action="get_channels", media_type=self.media_type, result=self.channels))

    def get_channel_list(self):
        val = ""

        for key in self.channels:
            val += key + "\n"
        
        return val
    
    def get_role(self, media_name):
        logging.info("'{guild_name}'\t{action}\t{media_type}\t'{media_name}'".format(guild_name=self.guild.name, action="get_role", media_type=self.media_type, media_name=media_name))

        if media_name in self.roles:
            role = self.roles[media_name]
        else:
            role = None

        logging.info("'{guild_name}'\t{action}\t{media_type}\t'{media_name}'\t'{result}'".format(guild_name=self.guild.name, action="get_role", media_type=self.media_type, media_name=media_name, result=role))
        return role

    def get_roles(self):
        logging.info("'{guild_name}'\t{action}\t{media_type}".format(guild_name=self.guild.name, action="get_roles", media_type=self.media_type))

        prefix = self.media_type + "-"
        prefix_len = len(prefix)

        for role in self.guild.roles:
            if role.name.startswith(prefix):
                media_name = role.name[prefix_len:]
                self.roles[media_name] = role
        
        logging.info("'{guild_name}'\t{action}\t{media_type}\t{result}".format(guild_name=self.guild.name, action="get_roles", media_type=self.media_type, result=self.roles))
    
    async def create_role(self, media_name):
        logging.info("'{guild_name}'\t{action}\t{media_type}\t'{media_name}'".format(guild_name=self.guild.name, action="create_role", media_type=self.media_type, media_name=media_name))

        role_name = "{media_type}-{media_name}".format(media_type=self.media_type, media_name=media_name)

        #TODO: Add Try\Catch Block
        #Create the role in the guild
        new_role = await self.guild.create_role(name=role_name)

        #Add the new role to our DB
        self.roles[media_name] = new_role

        logging.info("'{guild_name}'\t{action}\t{media_type}\t'{media_name}'\t{result}".format(guild_name=self.guild.name, action="create_role", media_type=self.media_type, media_name=media_name, result=new_role))
        return new_role
    
    async def create_missing_roles(self):
        logging.info("'{guild_name}'\t{action}\t{media_type}\t".format(guild_name=self.guild.name, action="create_missing_roles", media_type=self.media_type))
        
        for media_name in self.channels:
            #Check if the channel name has a role
            if media_name not in self.roles:
                new_role = await self.create_role(media_name)

                #Set Permissions on role
                await self.channels[media_name].set_permissions(new_role, read_messages=True, send_messages=True, read_message_history=True)
                logging.info("'{guild_name}'\t{action}\t{media_type}\t{media_name}\t{result}".format(guild_name=self.guild.name, action="create_missing_roles", media_type=self.media_type, media_name=media_name, result=new_role))