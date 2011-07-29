from exeapp.views.blocks.genericblock import GenericBlock

class FeedbackBlock(GenericBlock):
    use_common_content = True
    content_template = "exe/idevices/feedback/content.html"