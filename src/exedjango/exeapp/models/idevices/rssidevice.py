from django.db import models
from exeapp.models.idevices.idevice import Idevice
from exeapp.models.idevices import fields
from exeapp.models.idevices import feedparser
from exeapp.models.idevices.genericidevice import GenericIdevice


class RSSIdevice(GenericIdevice):
    
    name = "RSS"
    title = models.CharField(max_length=100, default=name)
    author = "Auchland University of Technology"
    purpose = """The RSS iDevice is used 
to provide new content to an individual users machine. Using this
iDevice you can provide links from a feed you select for learners to view."""
    emphasis = Idevice.NOEMPHASIS
    group = Idevice.COMMUNICATION
    icon = "icon_inter.gif"
    rss_url = fields.URLField(max_length=200, blank=True, default="",
                help_text="""Enter an RSS URL for the RSS feed you 
want to attach to your content. Feeds are often identified by a small graphic
 icon (often like this <img src="/static/images/feed-icon.png" />) or the text "RSS". Clicking on the 
 icon or text label will display an RSS feed right in your browser. You can copy and paste the
URL into this field. Alternately, right clicking on the link or graphic will open a menu box;
click on COPY LINK LOCATION or Copy Shortcut. Back in eXe open the RSS bookmark iDevice and Paste the URL 
into the RSS URL field and click the LOAD button. This will extract the titles from your feed and
display them as links in your content. From here you can edit the bookmarks and add
 instructions or additional learning information.""")
    content = fields.RichTextField(blank=True, default="")
    
    
    def load_rss(self, url):
        """
        Load the rss
        """
        self.rss_url = url
        content = ""
        try:
            rssDic = feedparser.parse(url)
            length = len(rssDic['entries'])
            if length > 0 :
                for i in range(0, length):
                    content += '<p><A href="%s">%s</A></P>' %(
                        rssDic['entries'][i].link, rssDic['entries'][i].title)          
        except IOError, error:
            content += _(u"Unable to load RSS feed from %s <br/>Please check the spelling and connection and try again.") % url
            
        if content == "":
            content += _(u"Unable to load RSS feed from %s <br/>Please check the spelling and connection and try again.") % url
        self.content = content
        
    class Meta:
        app_label = "exeapp"