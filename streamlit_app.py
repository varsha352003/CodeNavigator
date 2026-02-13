"""Streamlit Web UI for CodeNavigator - Semantic Code Search."""

import streamlit as st
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

from src.code_search.infrastructure.configuration import initialize_services, get_api_key
from src.code_search.application.commands import (
    IndexProjectCommand, IndexProjectCommandHandler,
    SearchCodeCommand, SearchCodeCommandHandler
)


# Page config
st.set_page_config(
    page_title="CodeNavigator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def get_score_class(score):
    """Get CSS class based on score."""
    if score >= 0.6:
        return "score-high"
    elif score >= 0.4:
        return "score-medium"
    else:
        return "score-low"


async def index_project_async(project_dir, api_key):
    """Index project asynchronously."""
    indexer, search_service = await initialize_services(api_key)
    index_handler = IndexProjectCommandHandler(indexer)
    
    index_command = IndexProjectCommand(project_directory=project_dir)
    await index_handler.handle(index_command)
    
    return indexer, search_service


async def search_code_async(search_service, query, max_results, threshold):
    """Search code asynchronously."""
    search_handler = SearchCodeCommandHandler(search_service)
    
    search_command = SearchCodeCommand(
        query=query,
        max_results_per_type=max_results,
        similarity_threshold=threshold
    )
    
    response = await search_handler.handle_text_search(search_command)
    return response


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<div class="main-header">🔍 CodeNavigator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Semantic Code Search powered by AI</div>', unsafe_allow_html=True)
    
    # Load environment
    load_dotenv()
    api_key = get_api_key()
    
    if not api_key:
        st.error("❌ OpenAI API key not found! Please add it to your .env file.")
        st.code("OPENAI_API_KEY=your-key-here")
        return
    
    # Sidebar - Project Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Project directory input
        st.subheader("📂 Project Directory")
        project_dir = st.text_input(
            "Enter project path:",
            value=r"C:\Users\Asus\Contacts\Desktop\Projects\CodeNavigator\src",
            help="Full path to the project you want to search"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            max_results = st.slider(
                "Max results per type:",
                min_value=1,
                max_value=10,
                value=5,
                help="Maximum number of files, classes, and methods to return"
            )
            
            threshold = st.slider(
                "Similarity threshold:",
                min_value=0.1,
                max_value=0.9,
                value=0.25,
                step=0.05,
                help="Minimum similarity score (lower = more results)"
            )
        
        # Index button
        st.markdown("---")
        if st.button("📊 Index Project", type="primary", use_container_width=True):
            # Validate directory
            if not project_dir or not Path(project_dir).exists():
                st.error("❌ Invalid project directory!")
            else:
                with st.spinner("🔄 Indexing project... This may take a moment."):
                    try:
                        indexer, search_service = asyncio.run(
                            index_project_async(project_dir, api_key)
                        )
                        st.session_state['search_service'] = search_service
                        st.session_state['indexed'] = True
                        st.session_state['project_dir'] = project_dir
                        st.success("✅ Project indexed successfully!")
                    except Exception as e:
                        st.error(f"❌ Indexing failed: {str(e)}")
        
        # Show indexing status
        if st.session_state.get('indexed'):
            st.success("✅ Ready to search")
            st.info(f"📂 {st.session_state.get('project_dir', 'N/A')}")
    
    # Main content area
    if not st.session_state.get('indexed'):
        st.info("👈 Please index a project first using the sidebar")
        
        # Example queries
        st.subheader("💡 Example Queries")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - `error handling`
            - `database connection`
            - `user authentication`
            - `validate email`
            """)
        with col2:
            st.markdown("""
            - `API endpoints`
            - `configuration settings`
            - `file upload`
            - `cache implementation`
            """)
        
        return
    
    # Search interface
    st.header("🔎 Search Your Code")
    
    # Search input
    query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., error handling, database connection, user login...",
        help="Use natural language to describe what you're looking for"
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.pop('last_results', None)
            st.rerun()
    
    # Perform search
    if search_clicked and query:
        with st.spinner("🔎 Searching..."):
            try:
                search_service = st.session_state['search_service']
                response = asyncio.run(
                    search_code_async(search_service, query, max_results, threshold)
                )
                st.session_state['last_results'] = response
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
                return
    
    # Display results
    if 'last_results' in st.session_state:
        response = st.session_state['last_results']
        
        # Results summary
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Results", response.total_results)
        with col2:
            st.metric("📁 Files", len(response.file_results))
        with col3:
            st.metric("🏗️ Classes", len(response.member_results))
        with col4:
            st.metric("⚙️ Methods", len(response.method_results))
        
        if response.total_results == 0:
            st.warning("No results found. Try adjusting your query or lowering the similarity threshold.")
            return
        
        st.markdown("---")
        
        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 All Results", "📁 Files", "🏗️ Classes", "⚙️ Methods"])
        
        with tab1:
            st.subheader("All Results (sorted by relevance)")
            for i, result in enumerate(response.all_results[:15], 1):
                score_class = get_score_class(result.score)
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{i}. [{result.type.upper()}] {result.name}**")
                        if result.type == "method" and result.member_name:
                            st.caption(f"↳ In class: {result.member_name}")
                        st.caption(f"📁 {result.file_path}")
                        if result.summary:
                            st.text(result.summary[:150] + ("..." if len(result.summary) > 150 else ""))
                    with col2:
                        st.markdown(f'<p class="{score_class}">Score: {result.score:.4f}</p>', 
                                  unsafe_allow_html=True)
                    st.markdown("---")
        
        with tab2:
            if response.file_results:
                for i, result in enumerate(response.file_results, 1):
                    score_class = get_score_class(result.score)
                    st.markdown(f"**{i}. {result.name}**")
                    st.caption(f"📁 {result.file_path}")
                    st.markdown(f'<span class="{score_class}">Score: {result.score:.4f}</span>', 
                              unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("No file results found.")
        
        with tab3:
            if response.member_results:
                for i, result in enumerate(response.member_results, 1):
                    score_class = get_score_class(result.score)
                    st.markdown(f"**{i}. {result.name}**")
                    st.caption(f"📁 {result.file_path}")
                    if result.summary:
                        st.text(result.summary[:150] + ("..." if len(result.summary) > 150 else ""))
                    st.markdown(f'<span class="{score_class}">Score: {result.score:.4f}</span>', 
                              unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("No class results found.")
        
        with tab4:
            if response.method_results:
                for i, result in enumerate(response.method_results, 1):
                    score_class = get_score_class(result.score)
                    st.markdown(f"**{i}. {result.name}**")
                    if result.member_name:
                        st.caption(f"↳ In class: {result.member_name}")
                    st.caption(f"📁 {result.file_path}")
                    if result.summary:
                        st.text(result.summary[:150] + ("..." if len(result.summary) > 150 else ""))
                    st.markdown(f'<span class="{score_class}">Score: {result.score:.4f}</span>', 
                              unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("No method results found.")


if __name__ == "__main__":
    # Initialize session state
    if 'indexed' not in st.session_state:
        st.session_state['indexed'] = False
    
    main()
