from .lspd import LSPD


def setup(bot):
    bot.add_cog(LSPD(bot))
