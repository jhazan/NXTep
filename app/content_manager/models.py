from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SocialMediaPlatform(models.Model):
    """Model representing a social media platform."""
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='platform_icons/', blank=True)
    api_credentials = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class ContentCategory(models.Model):
    """Model representing content categories."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Content Categories"
    
    def __str__(self):
        return self.name


class ContentItem(models.Model):
    """Model for managing content across social media and website."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    TYPE_CHOICES = [
        ('social', 'Social Media Post'),
        ('article', 'Blog Article'),
        ('page', 'Website Page'),
        ('email', 'Email Content'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Categorization
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    categories = models.ManyToManyField(ContentCategory, blank=True, related_name='content_items')
    
    # Media attachments
    featured_image = models.ImageField(upload_to='content_images/', blank=True)
    attachment = models.FileField(upload_to='content_attachments/', blank=True)
    
    # Publishing details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # For website content
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # If published for the first time
        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class SocialMediaPost(models.Model):
    """Model representing social media posts across platforms."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('failed', 'Failed'),
    ]
    
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='social_posts')
    platform = models.ForeignKey(SocialMediaPlatform, on_delete=models.CASCADE)
    custom_message = models.TextField(blank=True, help_text="Leave blank to use the content item's text")
    
    # Platform-specific data
    platform_post_id = models.CharField(max_length=100, blank=True)
    platform_post_url = models.URLField(blank=True)
    platform_specific_data = models.JSONField(blank=True, null=True)
    
    # Scheduling and status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(blank=True, null=True)
    posted_time = models.DateTimeField(blank=True, null=True)
    
    # Analytics
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    last_analytics_update = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-scheduled_time', '-posted_time']
    
    def __str__(self):
        return f"{self.platform.name} post - {self.content_item.title}"


class WebsiteSection(models.Model):
    """Model representing sections of the website."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class WebsitePage(models.Model):
    """Model representing website pages."""
    content_item = models.OneToOneField(ContentItem, on_delete=models.CASCADE, related_name='website_page')
    section = models.ForeignKey(WebsiteSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['section', 'order']
    
    def __str__(self):
        return self.content_item.title
