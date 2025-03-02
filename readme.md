# NXTep: MSP Management Platform

NXTep is a comprehensive platform for Managed Service Providers (MSPs) that combines CRM, network monitoring, content management, and billing functionalities in one integrated solution.

## Features

- **Client Management**: Track clients, contacts, and service agreements
- **Network Monitoring**: Monitor devices using SNMP and ping
- **Content Management**: Manage social media posts and website content
- **Billing System**: Create quotes and invoices with Stripe integration
- **Device-Based Pricing**: Track and bill customers based on managed devices

## Security Notice

This project uses environment variables for secure configuration. Never commit the `.env` file to version control. The repository includes a sample `.env.example` file that should be copied to `.env` and updated with secure values.

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nxtep.git
   cd nxtep
   ```

2. Copy the example environment file and update as needed:
   ```
   cp .env.example .env
   ```

3. Start the development environment:
   ```
   docker-compose up -d
   ```

4. Run migrations:
   ```
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application:
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

### Development Workflow

- Make changes to the Django code in the `app` directory
- Docker will automatically reload the application
- Run tests with: `docker-compose exec web python manage.py test`

## Project Structure

- `app/`: Django project root
  - `nxtep/`: Main Django project settings
  - `clients/`: Client management app
  - `monitoring/`: Network device monitoring app
  - `billing/`: Quotes and invoices app
  - `content_manager/`: Social media and website content management
  - `core/`: Shared functionality across apps

## Production Deployment

For production deployment, update the `.env` file with production values and ensure:

1. Set `DEBUG=0` in the environment
2. Use strong, unique passwords for all services
3. Configure proper SSL/TLS for all web traffic
4. Review all security settings in Django settings
5. Set up proper backup procedures for the database

## License

[Specify your license here]
