from exeapp.views.blocks.genericblock import GenericBlock


class RSSBlock(GenericBlock):
    edit_template = "exe/idevices/rss/edit.html"
    
    def process(self, action, data):
        if action == "Load":
            self.idevice.load_rss(data['rss_url'])
            self.idevice.save()
            return self.render()
        else:
            return super(RSSBlock, self).process(action, data)