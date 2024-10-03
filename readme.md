# Real Estate Investment Platform

## Overview

The Real Estate Investment Platform is a comprehensive web application designed to assist real estate investors in analyzing, managing, and optimizing their investment properties. Built with Flask and leveraging modern web technologies, this platform offers a suite of tools to streamline the real estate investment process.

## Features

- **Property Description Generator**: Automatically generate compelling property descriptions using AI and computer vision technology.
- **Cash Flow Calculator**: Calculate potential returns on investment properties.
- **ROI Calculator**: Analyze the return on investment for real estate ventures.
- **Property Comparison Tool**: Compare different properties side-by-side to make informed decisions.
- **Document Organizer**: Keep all your real estate documents organized and easily accessible.
- **Deal Analyzer**: Comprehensive tool for analyzing potential real estate deals.
- **Syndication Tool**: Manage and track syndication deals efficiently.
- **AI Assistant (Sha)**: Get tool-specific tips and advice from our AI assistant.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: SQLite
- **AI/ML**: GPT-4o mini for text generation, Computer Vision for image analysis
- **Authentication**: Flask-Login

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/nztinversive/Real-estate-app.git
   ```

2. Navigate to the project directory:
   ```
   cd Real-estate-app
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add necessary environment variables (e.g., API keys, database URLs)

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## Usage

After setting up the project, navigate to `http://localhost:5000` in your web browser to access the platform. Create an account to start using the various investment tools and features.

## Contributing

We welcome contributions to improve the Real Estate Investment Platform. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Project Link: [https://github.com/nztinversive/Real-estate-app](https://github.com/nztinversive/Real-estate-app)
