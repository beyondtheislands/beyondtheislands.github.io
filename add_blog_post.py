#!/usr/bin/env python3
import os
import sys
import re
from datetime import datetime

def read_blog_post(file_path):
    """Read blog post from a text file with expected format."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("Error: The file is empty.")
            return None
            
        title = lines[0].strip()
        content = lines[2:]  # Skip the first line (title) and the second line (empty)
        
        return title, content
    except Exception as e:
        print(f"Error reading blog post file: {e}")
        return None

def process_content(content_lines):
    """Process content lines to handle image links with alignment and natural paragraph flow."""
    img_pattern = re.compile(r'^(https?://\S+\.(jpg|jpeg|png|gif))\s+(left|center|right)$', re.IGNORECASE)
    
    # First, let's collect text paragraphs and images separately
    current_paragraph = []
    processed_blocks = []
    
    for line in content_lines:
        line = line.strip()
        
        # Check if this is an image line
        match = img_pattern.match(line)
        
        if match:
            # If we have accumulated text, add it as a paragraph first
            if current_paragraph:
                processed_blocks.append(('text', ' '.join(current_paragraph)))
                current_paragraph = []
            
            # Process the image
            img_url = match.group(1)
            alignment = match.group(3).lower()
            processed_blocks.append(('image', img_url, alignment))
        elif not line:  # Empty line marks paragraph break
            if current_paragraph:  # Only add paragraph if there's content
                processed_blocks.append(('text', ' '.join(current_paragraph)))
                current_paragraph = []
        else:  # Regular text line, add to current paragraph
            current_paragraph.append(line)
    
    # Don't forget the last paragraph if it exists
    if current_paragraph:
        processed_blocks.append(('text', ' '.join(current_paragraph)))
    
    # Now convert the blocks to HTML
    html_parts = []
    for block in processed_blocks:
        if block[0] == 'text':
            # Simple paragraph with the text
            html_parts.append(f'        <p>{block[1]}</p>')
        else:  # image
            img_url, alignment = block[1], block[2]
            img_html = f'        <div style="text-align: {alignment};">\n'
            img_html += f'            <img src="{img_url}" alt="Blog image" style="max-width: 100%;" />\n'
            img_html += '        </div>'
            html_parts.append(img_html)
            
    return "\n\n".join(html_parts)

def add_blog_post_to_html(blog_html_path, title, content):
    """Add a new blog post to the Blog.html file using simple string manipulation."""
    try:
        # Read the current Blog.html
        with open(blog_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check if a post with this title already exists to avoid duplicates
        if f'<h2>{title}</h2>' in html_content:
            print(f"Warning: A blog post with title '{title}' already exists. To avoid duplicates, please use a unique title.")
            return False
        
        # Get current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Create the new blog post HTML with proper indentation exactly matching Blog Post #1
        new_post_html = f'''
        <div class="blog-post">
            <h2>{title}</h2>
            <div class="blog-date">{current_datetime}</div>
            <div class="blog-body">
{content}
            </div>
        </div>
        
        <hr class="blog-divider" />

        '''
        
        # Find where to insert the new blog post - after the h1 and before the first blog post
        blog_content_start = html_content.find('<h1>Blog</h1>')
        if blog_content_start == -1:
            print("Error: Could not find the Blog heading in the HTML file.")
            return False
            
        # Move past the h1 tag
        content_start = blog_content_start + len('<h1>Blog</h1>')
        
        # Find the first blog post div (if any)
        first_blog_post = html_content.find('<div class="blog-post">', content_start)
        
        # If no blog posts exist yet, find the comment or container end
        if first_blog_post == -1:
            # Look for the comment about adding more posts
            comment_pos = html_content.find('<!-- Add more blog posts', content_start)
            if comment_pos != -1:
                insertion_point = html_content.rfind('\n', content_start, comment_pos) + 1
            else:
                # Insert before the container div closing tag
                container_end = html_content.find('</div>', content_start)
                if container_end == -1:
                    print("Error: Could not find a suitable insertion point in the HTML file.")
                    return False
                insertion_point = html_content.rfind('\n', content_start, container_end) + 1
        else:
            # Insert before the first blog post
            insertion_point = first_blog_post
        
        # Insert the new post HTML at the determined position
        updated_html = html_content[:insertion_point] + new_post_html + html_content[insertion_point:]
        
        # Write the updated HTML back to Blog.html
        with open(blog_html_path, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"Blog post '{title}' added successfully!")
        return True
    except Exception as e:
        print(f"Error updating HTML file: {e}")
        print(f"Exception details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_blog_post.py [path_to_blog_post_txt]")
        return
        
    blog_post_path = sys.argv[1]
    blog_html_path = '/Users/beyondtheislands/Documents/Development/beyondtheislands.github.io/Blog.html'
    
    # Verify files exist
    if not os.path.exists(blog_post_path):
        print(f"Error: Blog post file '{blog_post_path}' not found.")
        return
        
    if not os.path.exists(blog_html_path):
        print(f"Error: Blog.html file not found at '{blog_html_path}'.")
        return
    
    # Read and process the blog post
    result = read_blog_post(blog_post_path)
    if not result:
        return
        
    title, content_lines = result
    processed_content = process_content(content_lines)
    
    # Add the blog post to the HTML file
    add_blog_post_to_html(blog_html_path, title, processed_content)

if __name__ == "__main__":
    main()
