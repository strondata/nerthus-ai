#!/usr/bin/env python3
"""
Nerthus CLI - Command-line interface for Nerthus AI RAG system.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

import click
from dotenv import load_dotenv

from config import get_settings
from session import NerthusSession


# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    Nerthus - AI-powered RAG system with LangChain and ChromaDB.
    
    Biblioteca Python e CLI interativo que provê as capacidades de 
    inteligência, análise contextual e orquestração desenvolvidas 
    para o ecossistema Nerthus.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--collection', '-c', help='Collection name (optional)')
@click.option('--tag', '-t', multiple=True, help='Manual tag (repeatable)')
def ingest(path: str, collection: Optional[str], tag: Tuple[str, ...]):
    """
    Ingest documents from a file or directory.
    
    PATH: Path to a file or directory containing documents to ingest.
    
    Supported formats: PDF, TXT, DOCX, MD
    """
    click.echo(f"🔍 Starting ingestion from: {path}")
    
    try:
        # Initialize session
        session = NerthusSession()
        if collection:
            session.set_context(collection)
        session.initialize()
        
        # Determine if path is file or directory
        path_obj = Path(path)
        
        if path_obj.is_file():
            click.echo(f"📄 Ingesting file: {path_obj.name}")
            result = session.ingest_file(
                str(path),
                collection_name=collection,
                tags=list(tag),
            )
            
            if result["success"]:
                click.echo(f"✅ {result['message']}")
            else:
                click.echo(f"❌ Ingestion failed", err=True)
                sys.exit(1)
        
        elif path_obj.is_dir():
            click.echo(f"📁 Ingesting directory: {path_obj.name}")
            result = session.ingest_directory(
                str(path),
                collection_name=collection,
                tags=list(tag),
            )
            
            if result["success"]:
                click.echo(f"✅ {result['message']}")
                
                if result["files_processed"]:
                    click.echo("\nProcessed files:")
                    for file_info in result["files_processed"]:
                        click.echo(f"  • {Path(file_info['file']).name}: {file_info['chunks']} chunks")
                
                if result["errors"]:
                    click.echo(f"\n⚠️  {len(result['errors'])} files had errors:")
                    for error_info in result["errors"]:
                        click.echo(f"  • {Path(error_info['file']).name}: {error_info['error']}")
            else:
                click.echo(f"❌ Ingestion failed", err=True)
                sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('question')
@click.option('--collection', '-c', help='Collection name (optional)')
@click.option('--model', '-m', help='Model name (optional)')
@click.option('--verbose', '-v', is_flag=True, help='Show context sources')
def query(question: str, collection: Optional[str], model: Optional[str], verbose: bool):
    """
    Query the RAG system with a question.
    
    QUESTION: The question to ask the system.
    """
    click.echo(f"💭 Question: {question}\n")
    
    try:
        # Initialize session
        session = NerthusSession(model_name=model)
        if collection:
            session.set_context(collection)
        session.initialize()
        
        # Execute query
        with click.progressbar(length=1, label='Querying') as bar:
            result = session.query(question, collection_name=collection)
            bar.update(1)
        
        if result["success"]:
            click.echo(f"\n💡 Answer:\n{result['answer']}")
            click.echo(f"\n📚 Sources: {result['num_sources']} documents")
            
            if verbose and result["context"]:
                click.echo("\n📖 Context sources:")
                for i, ctx in enumerate(result["context"], 1):
                    click.echo(f"\n--- Source {i} ---")
                    click.echo(f"Content: {ctx['content'][:200]}...")
                    if ctx.get('metadata'):
                        click.echo(f"Metadata: {ctx['metadata']}")
        else:
            click.echo("❌ Query failed", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--collection', '-c', help='Collection name (optional)')
def interactive(collection: Optional[str]):
    """
    Start an interactive query session.
    """
    click.echo("🚀 Starting Nerthus interactive session...")
    click.echo("Type 'exit' or 'quit' to end the session.\n")
    
    try:
        # Initialize session
        session = NerthusSession()
        if collection:
            session.set_context(collection)
        session.initialize()
        
        # Show stats
        stats = session.get_stats()
        click.echo(f"📊 Session info:")
        click.echo(f"  • Model: {stats['model_name']}")
        click.echo(f"  • Collection: {stats['collection_name']}")
        click.echo(f"  • Documents: {stats['document_count']}")
        click.echo()
        
        # Interactive loop
        while True:
            try:
                question = click.prompt("Question", type=str)
                
                if question.lower() in ['exit', 'quit', 'q']:
                    click.echo("👋 Goodbye!")
                    break
                
                if not question.strip():
                    continue
                
                # Execute query
                result = session.query(question)
                
                if result["success"]:
                    click.echo(f"\n💡 {result['answer']}\n")
                else:
                    click.echo("❌ Query failed\n", err=True)
            
            except (KeyboardInterrupt, EOFError):
                click.echo("\n👋 Goodbye!")
                break
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--collection', '-c', help='Collection name (optional)')
def stats(collection: Optional[str]):
    """
    Show session and collection statistics.
    """
    try:
        session = NerthusSession()
        if collection:
            session.set_context(collection)
        session.initialize()
        
        stats = session.get_stats()
        
        click.echo("📊 Nerthus Statistics:")
        click.echo(f"\n🤖 Model Configuration:")
        click.echo(f"  • Model: {stats['model_name']}")
        click.echo(f"  • Temperature: {stats['temperature']}")
        
        click.echo(f"\n💾 Storage:")
        click.echo(f"  • Collection: {stats['collection_name']}")
        click.echo(f"  • Directory: {stats['persist_directory']}")
        click.echo(f"  • Documents: {stats['document_count']}")
        
        click.echo(f"\n📁 Supported formats:")
        formats = session.list_supported_formats()
        click.echo(f"  • {', '.join(formats)}")
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--collection', '-c', help='Collection name (optional)')
@click.confirmation_option(prompt='Are you sure you want to clear all documents?')
def clear(collection: Optional[str]):
    """
    Clear all documents from the collection.
    """
    try:
        session = NerthusSession()
        if collection:
            session.set_context(collection)
        session.initialize()
        
        result = session.clear_collection()
        
        if result["success"]:
            click.echo(f"✅ {result['message']}")
        else:
            click.echo(f"❌ {result['message']}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """
    Show current configuration.
    """
    try:
        settings = get_settings()
        
        click.echo("⚙️  Nerthus Configuration:")
        click.echo(f"\n🤖 LLM Settings:")
        click.echo(f"  • Model: {settings.model_name}")
        click.echo(f"  • Temperature: {settings.temperature}")
        click.echo(f"  • API Key: {'Set ✓' if settings.openai_api_key else 'Not set ✗'}")
        
        click.echo(f"\n💾 ChromaDB Settings:")
        click.echo(f"  • Persist Directory: {settings.chroma_persist_directory}")
        click.echo(f"  • Collection: {settings.collection_name}")
        click.echo("  • Available Collections:")
        for name, cfg in settings.available_collections.items():
            click.echo(f"    - {name}: {cfg.description}")
        
        click.echo(f"\n📄 RAG Settings:")
        click.echo(f"  • Chunk Size: {settings.chunk_size}")
        click.echo(f"  • Chunk Overlap: {settings.chunk_overlap}")
        click.echo(f"  • Top K Results: {settings.top_k_results}")
        click.echo(f"  • Report Context Documents: {settings.report_context_documents}")
        
        click.echo(f"\n📁 Paths:")
        click.echo(f"  • Prompts File: {settings.prompts_file}")
        click.echo(f"  • Documents Directory: {settings.documents_directory}")
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('name')
def context(name: str):
    """
    Set active collection context.
    """
    try:
        session = NerthusSession()
        session.set_context(name)
        click.echo(f"Contexto definido para: {name}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--type', 'report_type', required=True, help='Report type')
@click.option('--collection', '-c', help='Collection name (optional)')
def report(report_type: str, collection: Optional[str]):
    """
    Generate a report for a collection.
    """
    try:
        session = NerthusSession()
        if collection:
            session.set_context(collection)
        session.initialize()

        result = session.generate_report(report_type, filter_collection=collection)
        if result["success"]:
            click.echo(result["content"])
        else:
            click.echo("❌ Report generation failed", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()
