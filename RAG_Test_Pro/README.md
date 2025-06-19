# RAG Test Pro System - English Version

A comprehensive testing system for RAG (Retrieval-Augmented Generation) configurations with automatic API key management.

## ✅ Fixed Issues

- **All Hebrew text removed** - System now uses English only
- **Import errors fixed** - Corrected all module imports
- **Working system** - Fully functional interactive menu

## 🚀 Features

- **Question Set Management**: Load test questions from JSON files automatically
- **RAG Profile Configuration**: Built-in and custom profiles for different performance needs
- **Automatic API Key Rotation**: Smart key management to prevent rate limiting
- **Detailed Reporting**: Comprehensive test results with performance metrics
- **Interactive Menu**: User-friendly command-line interface

## 📋 Quick Start

1. **Navigate to directory**:

   ```bash
   cd RAG_Test_Pro
   ```

2. **Run the system**:

   ```bash
   python main.py
   ```

3. **Follow the menu** to:
   - View available question sets
   - Configure RAG profiles
   - Run test sessions
   - Create custom profiles
   - View results

## 🎯 RAG Parameters Available for Tuning

| **Parameter**          | **Range**  | **Description**              |
| ---------------------- | ---------- | ---------------------------- |
| `similarityThreshold`  | 0.3-0.9    | General similarity threshold |
| `maxChunks`            | 1-50       | Maximum chunks to retrieve   |
| `temperature`          | 0.0-1.0    | Model creativity level       |
| `chunkSize`            | 1000-4000  | Chunk size in characters     |
| `maxContextTokens`     | 4000-12000 | Maximum tokens for context   |
| `hybridSemanticWeight` | 0.4-0.8    | Semantic search weight       |
| `hybridKeywordWeight`  | 0.2-0.6    | Keyword search weight        |

## 📊 Running Tests

1. Select a question set from `test_questions/` directory
2. Choose a RAG profile (built-in or custom)
3. Confirm test execution
4. Monitor progress in real-time
5. Review detailed results and reports

## 📁 Directory Structure

```
RAG_Test_Pro/
├── main.py                  # Main system file
├── test_questions/          # JSON question files
├── rag_profiles/           # Custom RAG profiles
├── results/                # Test results and reports
└── README.md               # This file
```

## 🛠️ Built-in Profiles

- **Maximum Accuracy**: Optimized for highest accuracy, slower response
- **Fast Response**: Optimized for speed, good accuracy
- **Balanced Performance**: Balanced speed and accuracy

## 🔑 System Requirements

- Python 3.7+
- Access to the main project's AI modules
- Valid API keys configured in the system

## 📈 Version Information

- **Version**: 1.0 - English Only
- **Status**: All Hebrew text removed, imports fixed
- **Language**: English Only
- **Compatibility**: Works with existing RAG system

## 🎯 Status

✅ **Working**: System is fully functional  
✅ **English Only**: All Hebrew text removed  
✅ **Fixed Imports**: No more import errors  
✅ **Interactive Menu**: User-friendly interface

Ready for comprehensive RAG testing and optimization!
