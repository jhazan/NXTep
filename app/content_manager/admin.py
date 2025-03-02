from django.contrib import admin
from .models import (
    SocialMediaPlatform, 
    ContentCategory, 
    ContentItem,
    SocialMediaPost,
    WebsiteSection,
    WebsitePage
)


@admin.register(SocialMediaPlatform)
class SocialMediaPlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


class SocialMediaPostInline(admin.TabularInline):
    model = SocialMediaPost
    extra = 1
    fields = ('platform', 'custom_message', 'status', 'scheduled_time')


class WebsitePageInline(admin.StackedInline):
    model = WebsitePage
    extra = 0
    fields = ('section', 'order', 'is_published')


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'status', 'author', 'created_at', 'scheduled_for')
    list_filter = ('status', 'content_type', 'categories', 'author')
    search_fields = ('title', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'summary', 'content_type')
        }),
        ('Categorization', {
            'fields': ('categories',)
        }),
        ('Media', {
            'fields': ('featured_image', 'attachment')
        }),
        ('Publishing', {
            'fields': ('status', 'author', 'scheduled_for', 'created_at', 'updated_at', 'published_at')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SocialMediaPostInline, WebsitePageInline]


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ('content_item', 'platform', 'status', 'scheduled_time', 'posted_time')
    list_filter = ('status', 'platform', 'scheduled_time')
    search_fields = ('content_item__title', 'custom_message')
    readonly_fields = ('posted_time', 'platform_post_id', 'platform_post_url', 'likes', 'shares', 'comments', 'impressions', 'last_analytics_update')
    date_hierarchy = 'scheduled_time'
    
    fieldsets = (
        (None, {
            'fields': ('content_item', 'platform', 'custom_message')
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_time', 'posted_time')
        }),
        ('Platform Data', {
            'fields': ('platform_post_id', 'platform_post_url', 'platform_specific_data'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('likes', 'shares', 'comments', 'impressions', 'last_analytics_update'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebsiteSection)
class WebsiteSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(WebsitePage)
class WebsitePageAdmin(admin.ModelAdmin):
    list_display = ('content_item', 'section', 'order', 'is_published')
    list_filter = ('is_published', 'section')
    search_fields = ('content_item__title',)
