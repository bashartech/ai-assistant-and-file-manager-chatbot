from dotenv import load_dotenv
import os 
import asyncio
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool
from pathlib import Path
import webbrowser
from urllib.parse import quote_plus
import streamlit as st

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")
    st.stop()

# ==================== TOOL FUNCTIONS ====================

@function_tool
def create_folder(name: str) -> str:
    """Create a folder with the given name on the desktop."""
    path = Path.home() / "Desktop" / name
    try:
        path.mkdir(parents=True, exist_ok=False)
        return f"✅ Folder '{name}' created on Desktop"
    except FileExistsError:
        return f"⚠️ Folder '{name}' already exists on Desktop"
    except Exception as e:
        return f"❌ Error creating folder: {str(e)}"

@function_tool
def delete_folder(name: str) -> str:
    """Delete a folder with the given name from the desktop."""
    path = Path.home() / "Desktop" / name
    try:
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
            return f"✅ Folder '{name}' deleted from Desktop"
        else:
            return f"⚠️ '{name}' is not a valid folder on Desktop"
    except Exception as e:
        return f"❌ Failed to delete folder: {str(e)}"

@function_tool
def list_files(directory: str = None) -> str:
    """List files and folders in the specified directory."""
    if directory is None:
        directory = str(Path.home() / "Desktop")
    
    try:
        if not os.path.exists(directory):
            return f"❌ Directory '{directory}' does not exist"
        
        items = os.listdir(directory)
        if not items:
            return f"📁 Directory '{directory}' is empty"
        
        files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
        folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
        
        result = f"📂 Contents of '{directory}':\n\n"
        if folders:
            result += f"📁 **Folders ({len(folders)}):** {', '.join(folders)}\n\n"
        if files:
            result += f"📄 **Files ({len(files)}):** {', '.join(files)}"
        
        return result
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"

@function_tool
def read_file(path: str) -> str:
    """Read the content of a file."""
    try:
        if not os.path.isfile(path):
            return f"❌ '{path}' is not a valid file"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > 1000:
                return f"📄 **File content (first 1000 characters):**\n\n```\n{content[:1000]}...\n```\n\n*[File is longer, showing first 1000 characters]*"
            return f"📄 **File content:**\n\n```\n{content}\n```"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

@function_tool
def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        # Handle relative paths by making them absolute
        if not os.path.isabs(path):
            path = os.path.join(str(Path.home() / "Desktop"), path)
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Content written to {path}"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"

@function_tool
def delete_file(path: str) -> str:
    """Delete a file."""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"✅ File '{path}' deleted successfully"
        else:
            return f"⚠️ '{path}' does not exist or is not a file"
    except Exception as e:
        return f"❌ Error deleting file: {str(e)}"

@function_tool
def open_website(url: str) -> str:
    """Open a website in the default browser."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
        return f"🌐 Opened website: {url}"
    except Exception as e:
        return f"❌ Error opening website: {str(e)}"

@function_tool
def google_search(query: str) -> str:
    """Search Google and open the search results page."""
    try:
        encoded_query = quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(search_url)
        return f"🔍 Opened Google search for: '{query}'"
    except Exception as e:
        return f"❌ Error performing Google search: {str(e)}"

@function_tool
def youtube_search(query: str) -> str:
    """Search YouTube and open the search results page."""
    try:
        encoded_query = quote_plus(query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(youtube_url)
        return f"🎥 Opened YouTube search for: '{query}'"
    except Exception as e:
        return f"❌ Error performing YouTube search: {str(e)}"

@function_tool
def open_popular_websites(site_name: str) -> str:
    """Open popular websites by name."""
    popular_sites = {
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://www.twitter.com',
        'instagram': 'https://www.instagram.com',
        'linkedin': 'https://www.linkedin.com',
        'github': 'https://www.github.com',
        'stackoverflow': 'https://stackoverflow.com',
        'reddit': 'https://www.reddit.com',
        'wikipedia': 'https://www.wikipedia.org',
        'amazon': 'https://www.amazon.com',
        'netflix': 'https://www.netflix.com',
        'spotify': 'https://www.spotify.com',
        'gmail': 'https://mail.google.com',
        'drive': 'https://drive.google.com',
        'docs': 'https://docs.google.com',
        'sheets': 'https://sheets.google.com',
        'maps': 'https://maps.google.com',
        'translate': 'https://translate.google.com',
        'news': 'https://news.google.com',
        'weather': 'https://weather.com'
    }
    
    site_name_lower = site_name.lower()
    
    if site_name_lower in popular_sites:
        try:
            webbrowser.open(popular_sites[site_name_lower])
            return f"🌐 Opened {site_name}: {popular_sites[site_name_lower]}"
        except Exception as e:
            return f"❌ Error opening {site_name}: {str(e)}"
    else:
        available_sites = ', '.join(popular_sites.keys())
        return f"⚠️ '{site_name}' not found. Available sites: {available_sites}"

# ==================== AGENT INITIALIZATION ====================

@st.cache_resource
def initialize_agent():
    """Initialize the agent once and cache it"""
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    agent = Agent(
        name="FileManagerBot",
        instructions="""You are an enhanced file and folder manager with web browsing capabilities. You can:

FILE OPERATIONS:
- Create, delete, list, read, and write files and folders
- Manage files on the desktop and other directories

WEB OPERATIONS:
- Search Google for any topic
- Search YouTube for videos
- Open any website by URL
- Open popular websites by name (facebook, twitter, github, etc.)

When users ask you to search for something, use the appropriate search function.
When they want to open a website, use the open_website or open_popular_websites function.
Always be helpful and explain what you're doing.""",

        tools=[delete_folder, create_folder, list_files, read_file, write_file, delete_file, 
               open_website, google_search, youtube_search, open_popular_websites]
    )
    
    return agent, config

def extract_response_text(result):
    """Extract clean text from RunResult"""
    try:
        result_str = str(result)
        
        if "Final output (str):" in result_str:
            parts = result_str.split("Final output (str):")
            if len(parts) > 1:
                content = parts[1].strip()
                lines = content.split('\n')
                clean_lines = []
                for line in lines:
                    if line.startswith('- ') and ('new item' in line or 'raw response' in line):
                        break
                    clean_lines.append(line)
                return '\n'.join(clean_lines).strip()
        
        return result_str
    except Exception as e:
        return str(result)

# ==================== ASYNC RUNNER FUNCTION ====================

async def run_agent_async(agent, user_input, config):
    """Run the agent asynchronously"""
    try:
        response = await Runner.run(
            agent,
            input=user_input,
            run_config=config
        )
        return extract_response_text(response)
    except Exception as e:
        return f"❌ Error running agent: {str(e)}"

def run_agent_sync(agent, user_input, config):
    """Synchronous wrapper for the async agent runner"""
    try:
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_agent_async(agent, user_input, config))  # Executes the async function synchronously
            return result
        finally:
            loop.close()
    except Exception as e:
        return f"❌ Error in sync wrapper: {str(e)}"

# ==================== STREAMLIT UI ====================

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Web Browsing & File Manager Assistant")

# Initialize agent
agent, config = initialize_agent()

# Sidebar with instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    ### 📁 File Operations:
    - Create/delete folders on desktop
    - List files in directories
    - Read/write/delete files
    
    ### 🌐 Web Operations:
    - Search Google for any topic
    - Search YouTube for videos
    - Open websites by URL or name
    
    ### 💡 Example Commands:
    - "Create a folder called Projects"
    - "Search Google for machine learning"
    - "Open YouTube and search for tutorials"
    - "List files on my desktop"
    - "Open GitHub"
    - "Write hello world to a file called test.txt"
    """)
    
    st.markdown("---")
    st.markdown("**Popular Websites:**")
    st.markdown("facebook, twitter, instagram, linkedin, github, stackoverflow, reddit, wikipedia, amazon, netflix, spotify, gmail, drive, docs, sheets, maps, translate, news, weather")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [] # Streamlit's way to store data between interactions

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter your command..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Processing your request..."):
            try:
                # Use the synchronous wrapper
                clean_response = run_agent_sync(agent, prompt, config)
                st.markdown(clean_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": clean_response})
                
            except Exception as e:
                error_message = f"❌ Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


# Clear chat button
st.markdown("---")
if st.button("🗑️ Clear Chat", type="secondary"):
    st.session_state.messages = []
    st.rerun()

# Footer with debug info
st.markdown("---")
st.markdown("**💡 Tips:**")
st.markdown("- Type natural language commands like 'Create a folder called MyProject'")
st.markdown("- Use the quick action buttons for common tasks")
st.markdown("- The agent can handle both file operations and web browsing")
st.markdown("- All web operations will open in your default browser")

# Debug section (optional - can be removed)
with st.expander("🔧 Debug Info"):
    st.write(f"Desktop path: {Path.home() / 'Desktop'}")
    st.write(f"Current working directory: {os.getcwd()}")
    st.write(f"API Key present: {bool(gemini_api_key)}")