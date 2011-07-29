from exeapp.views.blocks.genericblock import GenericBlock


class ExternalURLBlock(GenericBlock):

    use_common_content = True
    content_template = "exe/idevices/externalurl/content.html"