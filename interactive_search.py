"""Fully interactive search script - Input project directory and queries via command prompt."""

import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

from src.code_search.infrastructure.configuration import initialize_services, get_api_key
from src.code_search.application.commands import (
    IndexProjectCommand, IndexProjectCommandHandler,
    SearchCodeCommand, SearchCodeCommandHandler
)


async def main():
    """Fully interactive search with project directory and query input."""
    load_dotenv()

    try:
        api_key = get_api_key()
        
        print("="*70)
        print("🔍 CODENAVIGATOR - Interactive Semantic Code Search")
        print("="*70)
        print(f"🔑 API key configured: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            print("\n❌ Error: OpenAI API key not found!")
            print("   Create a .env file with: OPENAI_API_KEY=your-key-here")
            return

        # Step 1: Get project directory from user
        print("\n" + "-"*70)
        print("📂 STEP 1: Enter the project directory to index")
        print("-"*70)
        print("Examples:")
        print("  • C:\\Users\\Asus\\Contacts\\Desktop\\Projects\\CodeNavigator\\src")
        print("  • D:\\MyProjects\\FlaskApp")
        print("  • C:\\Work\\API\\backend")
        print()
        
        while True:
            project_directory = input("📂 Project directory path: ").strip()
            
            if not project_directory:
                print("❌ Please enter a directory path")
                continue
            
            # Remove quotes if user pasted path with quotes
            project_directory = project_directory.strip('"').strip("'")
            
            # Check if directory exists
            project_path = Path(project_directory)
            if not project_path.exists():
                print(f"❌ Directory not found: {project_directory}")
                print("   Please enter a valid path")
                continue
            
            if not project_path.is_dir():
                print(f"❌ Not a directory: {project_directory}")
                continue
            
            print(f"\n✅ Directory found: {project_path.absolute()}")
            break

        # Initialize services
        print("\n🔧 Initializing services...")
        indexer, search_service = await initialize_services(api_key)
        index_handler = IndexProjectCommandHandler(indexer)
        search_handler = SearchCodeCommandHandler(search_service)

        # Step 2: Index the project
        print("\n" + "-"*70)
        print("📊 STEP 2: Indexing project")
        print("-"*70)
        print("⏳ This may take a moment depending on project size...")
        print("   (venv, node_modules, __pycache__ are automatically excluded)")
        print()
        
        index_command = IndexProjectCommand(project_directory=project_directory)
        await index_handler.handle(index_command)
        
        # Step 3: Interactive search
        print("\n" + "="*70)
        print("✅ INDEXING COMPLETE - Ready to search!")
        print("="*70)
        print("\n💡 Search Examples:")
        print("   • 'error handling'")
        print("   • 'database connection'")
        print("   • 'user authentication'")
        print("   • 'validate email'")
        print("   • 'API endpoints'")
        print("\n⚠️  Type 'exit', 'quit', or press Ctrl+C to stop")
        print("="*70)

        # Interactive search loop
        while True:
            print("\n" + "-"*70)
            query = input("🔍 Enter search query: ").strip()
            
            # Exit conditions
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                print("❌ Please enter a search query")
                continue
            
            # Perform search
            try:
                print(f"\n🔎 Searching for: '{query}'...")
                
                search_command = SearchCodeCommand(
                    query=query,
                    max_results_per_type=5,
                    similarity_threshold=0.25
                )
                
                response = await search_handler.handle_text_search(search_command)
                
                print(f"📊 Found {response.total_results} results in {response.execution_time_ms:.1f}ms")
                print("="*70)
                
                if response.total_results == 0:
                    print("\n❌ No results found.")
                    print("💡 Try:")
                    print("   • Different keywords")
                    print("   • More general terms")
                    print("   • Check if that functionality exists in the project")
                    continue
                
                # Display top 5 results
                for i, result in enumerate(response.all_results[:5], 1):
                    print(f"\n{i}. [{result.type.upper()}] {result.name}")
                    if result.type == "method" and result.member_name:
                        print(f"   ↳ In class: {result.member_name}")
                    print(f"   📁 File: {result.file_path}")
                    print(f"   🎯 Score: {result.score:.4f}")
                    if result.summary:
                        summary_preview = result.summary[:100]
                        if len(result.summary) > 100:
                            summary_preview += "..."
                        print(f"   📝 {summary_preview}")
                
                if response.total_results > 5:
                    print(f"\n... and {response.total_results - 5} more results")
                
            except Exception as e:
                print(f"\n❌ Search error: {e}")
                continue

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting CodeNavigator Interactive Search...\n")
    asyncio.run(main())
