# StockSage AI

StockSage AI is a modern, interactive web application for stock analysis and machine learning, built with Streamlit. It allows users to fetch or upload stock data, preprocess and engineer features, train and evaluate ML models, and visualize predictions—all with a beautiful, themeable interface.

## Features
- **Welcome Splash:** Fullscreen animated balloon welcome for 4 seconds on app start.
- **Theme Selection:** Choose from Zombie, Futuristic, Game of Thrones, and Gaming themes, each with a unique color scheme and transition animation.
- **Theme Transitions:** Fullscreen animated GIFs when switching themes for a smooth, immersive experience.
- **Data Loading:** Upload CSV or fetch stock data from Yahoo Finance.
- **Preprocessing & Feature Engineering:** Clean data, handle outliers, and generate technical indicators.
- **ML Pipeline:** Train regression, classification, or clustering models with scikit-learn.
- **Interactive Visualizations:** Beautiful charts and metrics with Plotly.
- **Downloadable Results:** Export predictions and analysis as CSV.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd StockSage_AI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **(Optional) Add your own GIFs:**
   - Place custom GIFs in the `assets/gifs/` folder if you want to personalize theme transitions.

## Usage
- On first launch, enjoy the welcome splash with balloons.
- Use the sidebar to select your preferred theme and navigate the ML pipeline steps.
- When switching themes, enjoy a fullscreen animated transition.
- Load your data, preprocess, engineer features, select and train a model, and visualize results.

## Requirements
See [`requirements.txt`](requirements.txt) for all dependencies and their versions.

## Credits
- Balloon and theme transition GIFs are from [Giphy](https://giphy.com/) and are used under their respective licenses:
  - Balloons: [Giphy Balloons](https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWE2aWpjOXVpZnVwbGltaHpxMHJsaXdyOGl3bzY5bnJ0N3J5aWhobSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eGmQlEGrVNuJYXvoXp/giphy.gif)
  - Gaming: [Giphy Gaming](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3dzejY5cDB0N2VsMXRwdnF4eW4xNjh0ZGxrZzg1Zm84bXA0bTVqcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ul3DvfCRQixLa/giphy.gif)
  - Futuristic: [Giphy Futuristic](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHhjdGQ1aWlqYmFidm5yeTlpcm94bnVhY3FkeWJxMTVqdm4yNzRpNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lbcLMX9B6sTsGjUmS3/giphy.gif)

## License
This project is for educational and personal use. Please respect the licenses of any third-party assets you use. 
