# Locale - P2P Skills Marketplace
## Product Requirements Document

## 1. Overview

Locale is a peer-to-peer skills marketplace that connects users needing services with verified local providers in Nigeria. The platform enables any user to seamlessly switch between being a buyer (requesting services) and seller (offering services) within a single unified profile, creating a flexible ecosystem where trust is built through social validation and secure transactions.

## 2. Problem Statement

In Nigeria's informal service economy, users face three core problems:
- **Trust Deficit**: Difficulty verifying service provider credibility and reliability
- **Accessibility**: Limited access to immediate, qualified local service providers
- **Payment Risk**: Financial insecurity when transacting with unknown individuals

Locale solves these through a unique combination of social vouching, real-time geospatial matching, and mandatory payment escrow.

## 3. Product Goals

### 3.1 Primary Objectives
- Establish the highest trust level through NIN verification and social vouching
- Provide near-instantaneous connection between users and nearby providers
- Ensure secure financial transactions via payment escrow
- Create a unified user experience for both buying and selling services

### 3.2 Success Metrics
- 90% successful job completion rate
- Average trust score of 75+ across active users
- Under 2-minute average response time for dispatch requests
- Less than 5% dispute rate on completed transactions

## 4. Core Features

### 4.1 Unified User Profile
- Single account capable of both buying and selling services
- Progressive verification system (Phone → NIN)
- Universal trust score reflecting overall platform reputation
- Ability to create multiple services across different categories

### 4.2 Social Vouching System
**Trusted Vouches**: +50 points from registered users
**Quick Vouches**: +10 points from non-users via OTP verification
**Activation Threshold**: 100 points required to activate a service
**Retraction Penalty**: -75 points for revoked vouches

### 4.3 Real-time Dispatch Engine
- Geospatial matching within 10km radius
- Multi-factor ranking (70% proximity, 30% trust score)
- Simultaneous offers to top 3 providers
- 60-second acceptance window with first-come priority

### 4.4 Payment Escrow System
- Funds held securely until service completion
- Buyer confirmation required for fund release
- Manual dispute resolution by administrators
- Support for partial refunds and negotiated settlements

## 5. User Journey

### 5.1 Registration & Onboarding
1. User provides basic information (name, email, phone, password)
2. Phone verification via OTP (Level 0 access)
3. Optional NIN submission for Level 1 verification
4. NIN securely hashed and stored (never plaintext)

### 5.2 Service Creation Flow
1. Level 1 user creates service (initially inactive)
2. Shares unique vouch links with network
3. Collects trust points from vouches
4. Service auto-activates at 100-point threshold
5. Service appears in search and dispatch results

### 5.3 Dispatch Request Flow
1. Buyer selects service category and shares location
2. System finds nearby available providers using Redis geospatial queries
3. Ranks providers by proximity and trust score
4. Sends real-time offers via WebSocket
5. First provider to accept gets the job
6. Buyer pays into escrow
7. Provider performs service
8. Buyer confirms completion
9. Funds released to provider

## 6. Technical Architecture

### 6.1 Technology Stack
- **Frontend**: idk fr
- **Backend**: FastAPI (Python) for high-performance async operations
- **Database**: PostgreSQL
- **Real-time**: WebSockets for live communication
- **Payments**: Paystack  integration
- **SMS**: OTP delivery

### 6.2 Core Data Model

**User Entity**
- Unified model for both buyers and sellers
- Verification levels (0: phone, 1: NIN)
- Universal trust score based on completed jobs and reviews
- Ability to create multiple services

**Service Entity**
- Represents a specific skill offering
- Independent trust points from vouches
- Real-time location and availability status
- Category-based classification

**Job Entity**
- Links buyer and service (through seller)
- Supports both dispatch (immediate) and scheduled types
- State machine tracking from creation to completion
- Payment and review associations

### 6.3 Key API Endpoints

**Authentication**
- `POST /auth/register` - User registration with phone
- `POST /auth/verify-phone` - OTP verification
- `POST /auth/login` - JWT token generation

**User Management**
- `PUT /users/me` - Profile updates including NIN submission
- `GET /users/me` - Current user profile with trust score

**Service Management**
- `POST /services` - Create new service offering
- `POST /services/{id}/vouch` - Request vouch for service
- `GET /services` - Browse and search services

**Job Management**
- `POST /jobs/dispatch` - Request immediate service
- `POST /jobs/{id}/accept` - Provider accepts job offer
- `POST /jobs/{id}/complete` - Mark job as finished
- `POST /jobs/{id}/confirm` - Buyer confirms completion

**Payment Processing**
- `POST /jobs/{id}/pay` - Initiate escrow payment
- `POST /payments/webhook` - Payment gateway callbacks

## 7. Security & Compliance

### 7.1 Data Protection
- NIN information hashed using bcrypt before storage
- Phone numbers hashed for privacy in quick vouches
- Payment data handled exclusively through certified gateways
- Regular security audits and penetration testing

### 7.2 Financial Security
- PCI DSS compliance through payment gateway integration
- Escrow protection for all transactions
- Comprehensive audit trails for financial activities
- Manual oversight for dispute resolution

### 7.3 Platform Security
- JWT-based stateless authentication
- Rate limiting on sensitive endpoints
- Input validation through Pydantic models
- CORS policies for web client protection

## 8. Deployment Strategy

### 8.1 MVP Deployment
- Single FastAPI application instance
- Managed PostgreSQL with PostGIS extension
- Redis for caching and geospatial queries
- Vue.js frontend hosted on CDN
- Load balancer with SSL termination

### 8.2 Scaling Considerations
- Horizontal scaling of stateless API servers
- Database read replicas for search and browse operations
- Redis clustering for geospatial performance
- Background workers for async notifications

## 9. Business Model

### 9.1 Revenue Streams
- **Transaction Commission**: 5-10% on completed job value
- **Premium Features**: Enhanced visibility and analytics (future)
- **Enterprise Solutions**: Business accounts (future)

### 9.2 Cost Structure
- Payment gateway transaction fees
- SMS delivery costs for OTP and notifications
- Cloud infrastructure and hosting
- Customer support and dispute resolution

## 10. Go-to-Market Strategy

### 10.1 Launch Focus
- Initial geographic focus on specific Lagos LGAs
- Home services category (plumbing, electrical, cleaning)
- Progressive expansion to other regions and categories
- Community-driven growth through vouch networks

### 10.2 User Acquisition
- Referral incentives for successful vouches
- Local community partnerships
- Digital marketing targeting urban professionals
- Word-of-mouth through successful service experiences

## 11. Risk Mitigation

### 11.1 Operational Risks
- Manual dispute resolution for MVP to ensure quality
- Progressive trust building to prevent fraud
- Comprehensive provider verification processes
- 24/7 monitoring for platform issues

### 11.2 Market Risks
- Focus on high-demand home service categories
- Localized launch to validate product-market fit
- Flexible pricing based on market rates
- Continuous user feedback integration

## 12. Future Roadmap

### 12.1 Post-MVP Enhancements
- Mobile applications for iOS and Android
- Advanced scheduling with calendar integration
- AI-powered matching and recommendations
- Service guarantees and insurance products
- Multi-city and international expansion

### 12.2 Technical Evolution
- Microservices architecture for scalability
- Event-driven systems for better decoupling
- Advanced analytics and business intelligence
- Automated dispute resolution systems

## 13. Conclusion

Locale represents a paradigm shift in peer-to-peer service marketplaces by prioritizing community validation over centralized verification. The unified user model creates a dynamic ecosystem where trust is earned through successful interactions and social proof, while the technical architecture ensures security, performance, and scalability for sustainable growth in the Nigerian market and beyond.