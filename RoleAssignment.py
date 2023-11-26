import nextcord
from nextcord.ext import commands
import sqlite3

class RoleAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Connect to the database
        self.conn = sqlite3.connect('roles.db')
        self.c = self.conn.cursor()

        # Create the table if it doesn't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS role_assignment
             (server_id INTEGER, role_id INTEGER)''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Get role data from the database
        self.c.execute('SELECT role_id FROM role_assignment WHERE server_id=?', (member.guild.id,))
        role_id = self.c.fetchone()

        if role_id:
            role = nextcord.utils.get(member.guild.roles, id=role_id[0])
            await member.add_roles(role)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setrole(self, ctx, role_id):
        """
        **`.setrole <Айди роли>`**
        """
        role_id = int(role_id)

        # Remove the old role if exists
        old_role_id = self.get_role_assignment(ctx.guild.id)
        if old_role_id:
            old_role = nextcord.utils.get(ctx.guild.roles, id=old_role_id)
            await ctx.author.remove_roles(old_role)

        # Write/update role data in the database
        self.c.execute('INSERT OR REPLACE INTO role_assignment (server_id, role_id) VALUES (?, ?)', (ctx.guild.id, role_id))
        self.conn.commit()

        # Assign the new role
        new_role = nextcord.utils.get(ctx.guild.roles, id=role_id)
        await ctx.author.add_roles(new_role)
        await ctx.send(f'<a:yes:1173982104393105478> Роль установлена ​​на <@&{role_id}>')

    def get_role_assignment(self, server_id):
        self.c.execute('SELECT role_id FROM role_assignment WHERE server_id=?', (server_id,))
        result = self.c.fetchone()
        return result[0] if result else None

def setup(bot):
    bot.add_cog(RoleAssignment(bot))
