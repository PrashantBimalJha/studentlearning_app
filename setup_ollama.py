#!/usr/bin/env python3
"""
🎓 Learning App - Ollama Setup Script
This script helps set up Ollama for AI chat support
"""

import subprocess
import sys
import platform
import requests
import time
import os

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🎓 LEARNING APP - OLLAMA SETUP")
    print("=" * 60)
    print("This script will help you set up Ollama for AI chat support")
    print()

def check_ollama_installed():
    """Check if Ollama is already installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is already installed!")
            print(f"   Version: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Ollama is not installed")
    return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    print(f"🖥️  Detected operating system: {system}")
    print()
    
    if system == "darwin":  # macOS
        print("📥 Installing Ollama for macOS...")
        print("Please run the following command in your terminal:")
        print("curl -fsSL https://ollama.ai/install.sh | sh")
        print()
        print("Or download from: https://ollama.ai/download")
        
    elif system == "linux":
        print("📥 Installing Ollama for Linux...")
        print("Please run the following command in your terminal:")
        print("curl -fsSL https://ollama.ai/install.sh | sh")
        print()
        print("Or download from: https://ollama.ai/download")
        
    elif system == "windows":
        print("📥 Installing Ollama for Windows...")
        print("Please download and install from: https://ollama.ai/download")
        print("Or use Windows Subsystem for Linux (WSL)")
        
    else:
        print(f"❌ Unsupported operating system: {system}")
        print("Please visit https://ollama.ai/download for installation instructions")
        return False
    
    return True

def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    try:
        # Try to start Ollama in the background
        if platform.system().lower() == "windows":
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        print("⏳ Waiting for Ollama to start...")
        time.sleep(5)
        
        # Check if Ollama is running
        if check_ollama_running():
            print("✅ Ollama service started successfully!")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def pull_llama_model():
    """Pull the Llama model for AI chat"""
    print("📦 Pulling Llama model (this may take a few minutes)...")
    print("   Model: llama3.2")
    print("   Size: ~2GB")
    print()
    
    try:
        # Start the pull process
        process = subprocess.Popen(['ollama', 'pull', 'llama3.2'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, 
                                 text=True, 
                                 bufsize=1, 
                                 universal_newlines=True)
        
        # Show progress
        for line in process.stdout:
            if "pulling" in line.lower() or "downloading" in line.lower():
                print(f"   {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Llama model downloaded successfully!")
            return True
        else:
            print("❌ Failed to download Llama model")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def test_ai_chat():
    """Test the AI chat functionality"""
    print("🧪 Testing AI chat functionality...")
    
    try:
        # Test with a simple question
        test_data = {
            "model": "llama3.2",
            "prompt": "Hello! Can you help me with math?",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=test_data, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '')
            if ai_response:
                print("✅ AI chat is working!")
                print(f"   Test response: {ai_response[:100]}...")
                return True
        
        print("❌ AI chat test failed")
        return False
        
    except Exception as e:
        print(f"❌ Error testing AI chat: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print()
        if not install_ollama():
            print("❌ Setup failed. Please install Ollama manually.")
            return False
        
        print()
        input("Press Enter after installing Ollama to continue...")
        print()
    
    # Check if Ollama is running
    if not check_ollama_running():
        print()
        if not start_ollama_service():
            print("❌ Setup failed. Please start Ollama manually.")
            print("   Run: ollama serve")
            return False
    else:
        print("✅ Ollama service is already running!")
    
    print()
    
    # Pull the model
    if not pull_llama_model():
        print("❌ Setup failed. Please pull the model manually.")
        print("   Run: ollama pull llama3.2")
        return False
    
    print()
    
    # Test AI chat
    if not test_ai_chat():
        print("❌ Setup failed. AI chat is not working properly.")
        return False
    
    print()
    print("=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Ollama is installed and running")
    print("✅ Llama model is downloaded")
    print("✅ AI chat is working")
    print()
    print("🚀 You can now use the AI Chat feature in the Learning App!")
    print("   Go to: http://localhost:5000/chat")
    print()
    print("💡 Tips:")
    print("   - Keep Ollama running: ollama serve")
    print("   - Available models: ollama list")
    print("   - Pull more models: ollama pull <model-name>")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)
