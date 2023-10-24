from modeltranslation.translator import register, TranslationOptions
from .models import Feature, DataType, VizMark, VizType, VizInput, UploadFile, DataTypeRule, VizTypeMark, \
VizInputFeature, VizOutput, Project, VizGoal, DataPortal, PlatformPortal, Feedback, Theme, Like, ProjectStatus, \
SubscribeDataArea, SubscribeDataProject


@register(ProjectStatus)
class ProjectStatusTranslationOptions(TranslationOptions):
    fields = ('name', )

@register(Theme)
class ThemeTranslationOptions(TranslationOptions):
    fields = ('name', )
