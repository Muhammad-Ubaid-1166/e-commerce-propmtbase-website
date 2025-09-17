# Fashion Wear - AI-Powered E-commerce Platform

A modern Django-based e-commerce website featuring AI-powered product management and an intelligent shopping assistant.

## 🌟 Features

### Core E-commerce Functionality
- **Product Catalog**: Browse and search fashion products with dynamic filtering
- **Shopping Cart**: Add products to cart with real-time counter updates
- **Responsive Design**: Mobile-first design with Bootstrap 5.3.3
- **Image Management**: Product image upload and display capabilities

### AI-Powered Features
- **AI Product Assistant**: Interactive AI chat for product recommendations and fashion advice
- **Intelligent Product Creation**: Add products through natural language conversations
- **Smart Product Retrieval**: AI-powered product search and discovery
- **Conversational Interface**: Natural language processing for user interactions

### User Experience
- **Modern UI/UX**: Clean, professional design with gradient themes
- **Interactive Elements**: Smooth animations and hover effects
- **Search Functionality**: Real-time product search with filtering
- **Notification System**: Toast notifications for user feedback

## 🛠️ Technology Stack

### Backend
- **Django 4.x**: Python web framework
- **SQLite**: Default database (configurable)
- **Pillow**: Image processing for product photos
- **Decimal**: Precise price calculations

### Frontend
- **Bootstrap 5.3.3**: Responsive CSS framework
- **Font Awesome 6.0**: Icon library
- **Google Fonts**: Inter & Playfair Display typography
- **Vanilla JavaScript**: Interactive functionality

### AI Integration
- **Gemini 2.0 Flash**: Google's AI model for natural language processing
- **Custom Agent System**: Specialized agents for product management
- **Pydantic**: Data validation and serialization

## 📦 Installation

### Prerequisites
- Python 3.11+
- Django 4.x
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fashion-wear
   ```

2. **Install dependencies**
   ```bash
   pip install django pillow python-dotenv
   pip install agents  # AI agents library
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser  # Optional: create admin user
   ```

5. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

## 🗂️ Project Structure

```
fashion-wear/
├── fashion_wear/          # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Project configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI configuration
├── shop/                 # Main application
│   ├── agents_logic/     # AI agent system
│   │   └── agent_service.py  # AI processing logic
│   ├── templates/shop/   # HTML templates
│   │   └── index.html    # Main template
│   ├── static/shop/      # Static assets
│   │   ├── styles.css    # Custom styles
│   │   ├── responsive.css # Mobile styles
│   │   └── images/       # Product images
│   ├── models.py         # Data models
│   ├── views.py          # View controllers
│   ├── urls.py           # App URL patterns
│   └── forms.py          # Django forms
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## 🤖 AI Features

### Product Management Agent
- **Natural Language Processing**: Understands product creation requests
- **Data Extraction**: Automatically extracts product details from conversation
- **Validation**: Ensures required information is provided
- **Integration**: Seamlessly creates products in the database

### Conversation System
- **Session Management**: Tracks user conversations
- **Context Awareness**: Maintains conversation context
- **Error Handling**: Graceful error recovery and user feedback

## 🎨 UI Components

### Navigation
- Responsive navbar with AI search toggle
- Mobile-friendly offcanvas menu
- Shopping cart counter with animations

### Product Cards
- Hover effects and smooth transitions
- Product image handling with fallbacks
- Add to cart functionality
- Price and description display

### AI Interface
- Sliding search panel from top
- Quick action buttons for common queries
- Real-time chat responses
- Typing indicators and loading states

## 📱 Responsive Design

The website is fully responsive and optimized for:
- **Desktop**: Full feature experience
- **Tablet**: Adapted layout and navigation
- **Mobile**: Touch-friendly interface with collapsed menus

## 🔧 Configuration

### Django Settings
- **Allowed Hosts**: Configured for development and deployment
- **Static Files**: Organized with proper URL patterns
- **Media Files**: Image upload handling
- **CSRF Protection**: Secured for API endpoints

### AI Configuration
- **Model Selection**: Gemini 2.0 Flash for optimal performance
- **Agent Instructions**: Specialized prompts for e-commerce context
- **Error Handling**: Robust error recovery mechanisms

## 🚀 Deployment

### Development
```bash
python manage.py runserver 0.0.0.0:5000
```

### Production Considerations
- Set `DEBUG=False` in production
- Configure proper database (PostgreSQL recommended)
- Set up static file serving (nginx/Apache)
- Configure environment variables securely
- Enable HTTPS and security headers

## 🔐 Security Features

- **CSRF Protection**: Built-in Django CSRF middleware
- **Input Validation**: Pydantic models for data validation
- **File Upload Security**: Image validation and secure storage
- **Environment Variables**: Sensitive data in `.env` files

## 📊 Database Models

### Product Model
- `product_id`: Unique identifier
- `name`: Product name
- `price`: Decimal field for accurate pricing
- `description`: Product details
- `image`: Product photo upload
- `created_at`/`updated_at`: Timestamps

### Conversation Model
- `user_message`: User input
- `agent_response`: AI response
- `session_id`: Session tracking
- `timestamp`: Conversation time

## 🔄 API Endpoints

- `GET /`: Main page with product listing
- `POST /chat/`: AI chat interface
- `GET /trigger-retrieve/`: Product retrieval from AI response
- `GET /create-product/`: Product creation form
- `/admin/`: Django admin panel

## 🎯 Future Enhancements

- User authentication and profiles
- Order management system
- Payment integration (Stripe/PayPal)
- Advanced product filtering
- Wishlist functionality
- Review and rating system
- Inventory management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments for implementation details

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive design system
- Google for the Gemini AI model
- Font Awesome for the icon library

---

**Note**: This is a demonstration project showcasing AI integration with Django e-commerce functionality. For production use, additional security measures and testing should be implemented.
