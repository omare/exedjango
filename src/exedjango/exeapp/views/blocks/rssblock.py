from exeapp.views.blocks.genericblock import GenericBlock


class RSSBlock(GenericBlock):
    
    def process(self, action, data):
        if action == "Load":
            self.idevice.load_rss(data['rss_url'])
            self.idevice.save()
            return self.render()
        else:
            return super(RSSBlock, self).process(action, data)