from django.db import models
from exeapp.models.idevices.genericidevice import GenericIdevice
from exeapp.models.idevices.idevice import Idevice
import urllib
from BeautifulSoup import  BeautifulSoup
import re
from exe.engine.path import TempDirPath

class UrlOpener(urllib.FancyURLopener):
    """
    Set a distinctive User-Agent, so Wikipedia.org knows we're not spammers
    """
    version = "eXe/exe@exelearning.org"
urllib._urlopener = UrlOpener()

def _(value):
    return value

class WikipediaIdevice(GenericIdevice):
    name = "Wiki Article"
    title = models.CharField(max_length=100, default=name)
    author = "University of Auckland" 
    purpose = """<p>The Wikipedia iDevice allows you to locate 
existing content from within Wikipedia and download this content into your eXe 
resource. The Wikipedia Article iDevice takes a snapshot copy of the article 
content. Changes in Wikipedia will not automatically update individual snapshot 
copies in eXe, a fresh copy of the article will need to be taken. Likewise, 
changes made in eXe will not be updated in Wikipedia. </p> <p>Wikipedia content 
is covered by the GNU free documentation license.</p>""" 
    emphasis = Idevice.NoEmphasis
    group = Idevice.Content
    article_name = models.CharField(max_length=100, blank=True, default="",
                        help_text="""Enter a phrase or term you wish to search 
within Wikipedia.""")
    content = models.TextField(blank=True, default="")
    site = "http://en.wikipedia.org/wiki/"
    icon = u"icon_inter.gif"
    userResources = []
    # TODO FDL has to be in the package
    #systemResources += ["fdl.html"]
    #    self._langInstruc      = x_(u"""Select the appropriate language version 
#of Wikipedia to search and enter search term.""")

    def load_article(self, title):
        """
        Load the article from Wikipedia
        """
        self.articleName = title
        url = ""
        title = urllib.quote(title.replace(" ", "_").encode('utf-8'))
        try:
            url  = (self.site or self.ownUrl)
            if not url.endswith('/') and title <> '': url += '/'
            if '://' not in url: url = 'http://' + url
            url += title
            net  = urllib.urlopen(url)
            page = net.read()
            net.close()
        except IOError, error:
            self.content = _(u"Unable to download from %s <br/>Please check the spelling and connection and try again.") % url
            self.content_w_resourcePaths = self.content
            self.content_wo_resourcePaths = self.content
            return

        page = unicode(page, "utf8")
        # FIXME avoid problems with numeric entities in attributes
        page = page.replace(u'&#160;', u'&nbsp;')

        # avoidParserProblems is set to False because BeautifulSoup's
        # cleanup was causing a "concatenating Null+Str" error,
        # and Wikipedia's HTML doesn't need cleaning up.
        # BeautifulSoup is faster this way too.
        soup = BeautifulSoup(page, False)
        content = soup.first('div', {'id': "content"})

        # remove the wiktionary, wikimedia commons, and categories boxes
        #  and the protected icon and the needs citations box
        if content:
            infoboxes = content.findAll('div',
                    {'class' : 'infobox sisterproject'})
            [infobox.extract() for infobox in infoboxes]
            catboxes = content.findAll('div', {'id' : 'catlinks'})
            [catbox.extract() for catbox in catboxes]
            amboxes = content.findAll('table',
                    {'class' : re.compile(r'.*\bambox\b.*')})
            [ambox.extract() for ambox in amboxes]
            protecteds = content.findAll('div', {'id' : 'protected-icon'})
            [protected.extract() for protected in protecteds]
        else:
            content = soup.first('body')

        if not content:
            self.content = _(u"Unable to download from %s <br/>Please check the spelling and connection and try again.") % url
            # set the other elements as well
            return
        
        bits = url.split('/')
        netloc = '%s//%s' % (bits[0], bits[2])
        self.content = self.reformatArticle(netloc, unicode(content))
        # now that these are supporting images, any direct manipulation
        # of the content field must also store this updated information
        # into the other corresponding fields of TextAreaField:
        # (perhaps eventually a property should be made for TextAreaField 
        #  such that these extra set's are not necessary, but for now, here:)

    def reformatArticle(self, netloc, content):
        """
        Changes links, etc
        """
        content = re.sub(r'href="/', r'href="%s/' % netloc, content)
        content = re.sub(r'<(span|div)\s+(id|class)="(editsection|jump-to-nav)".*?</\1>', '', content)
        #TODO Find a way to remove scripts without removing newlines
        content = content.replace("\n", " ")
        content = re.sub(r'<script.*?</script>', '', content)
        return content
        
    class Meta:
        app_label = "exeapp"
        


    
