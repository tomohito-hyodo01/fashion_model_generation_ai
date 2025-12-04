# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Virtual Fashion Try-On: A Windows desktop application that generates images and videos of fashion models wearing specified garments. Built with PySide6 (Qt6) for the UI and integrates multiple AI providers for image/video generation.

## Development Commands

```bash
# Run the application
python app/main.py

# Run tests
pytest

# Build Windows executable
powershell -ExecutionPolicy Bypass -File scripts/pack_win.ps1

# Code formatting
black .

# Linting
ruff check .
```

## Architecture

### Multi-Page UI Structure
The application uses a QStackedWidget-based navigation with a side menu:
- **HomeScreen** (`ui/screens/home_screen.py`): Landing page with navigation cards
- **GenerationScreen** (`ui/screens/generation_screen.py`): Image generation with garment upload, model attributes, and settings
- **EditScreen** (`ui/screens/edit_screen.py`): History browser, gallery view, and chat-based image refinement

### MainWindow (`ui/main_window.py`)
Central orchestrator (~2100 lines) that:
- Manages screen navigation via `QStackedWidget`
- Contains all Worker threads for async operations
- Bridges signals between screens and backend
- Handles API adapter creation and lifecycle

### Provider Adapters (`core/adapters/`)
All adapters inherit from `ProviderBase` and implement:
- `generate()`: Main image generation
- `prepare()`: Request preparation
- `check_api_status()`: API connectivity check

Available providers:
- `GeminiImagenAdapter`: Google Gemini 2.5 Flash (primary, supports image reference)
- `OpenAIAdapter`: DALL-E 3
- `StabilityAdapter`: Stability AI SD 3.5
- `VertexAdapter`: Google Vertex AI Imagen
- `FashnTryonAdapter`: FASHN virtual try-on
- `FashnVideoAdapter`: FASHN video generation

### Worker Threads
Background operations run in QThread workers defined in `main_window.py`:
- `GenerationWorker`: Image generation
- `ChatRefinementWorker`: Chat-based image editing
- `VideoGenerationWorker`: Video creation
- `FashnTryonWorker`: Virtual try-on processing
- `ReferencePersonWorker`: Reference person mode with face swap

### Styling System (`ui/styles.py`, `ui/themes.py`)
Centralized theming with:
- `Colors`: Color constants
- `Fonts`: Typography settings
- `Spacing`, `BorderRadius`: Layout constants
- `Styles`: Pre-built QSS stylesheets (BUTTON_PRIMARY, BUTTON_SECONDARY, etc.)

### Data Models (`models/`)
- `ClothingItem`: Garment with image, category, color
- `ModelAttributes`: Age, gender, body type, pose, background
- `GenerationConfig`: Size, count, mode settings

## Key Patterns

### PyInstaller Asset Path Resolution
When accessing assets in packaged builds:
```python
def get_asset_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path
```

### Signal-Based Communication
Screens emit signals that MainWindow connects to backend operations:
```python
# Screen emits
self.generation_requested.emit(params)

# MainWindow connects
self.generation_screen.generation_requested.connect(self._on_generation_requested)
```

### Progress Updates
Workers emit progress via signals; UI updates through `set_progress()` / `hide_progress()` methods on screens.

## Important Constraints

- **Backend logic stays in MainWindow**: Worker classes, API adapter creation, and history management remain in `main_window.py`
- **UI-only changes**: When modifying screens, do not change backend logic
- **Windows-specific**: Uses DPAPI for API key encryption, ctypes for taskbar icon support
