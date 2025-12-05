# Dallas Restaurants Dashboard — Project Documentation

## a. Project Overview and Scope

**Project Title:** Dallas Restaurants Dashboard  

**Motivation & Background:**  
Dallas is a vibrant city with a diverse culinary scene. Residents and visitors often struggle to find reliable, up-to-date information about restaurants, their offerings, and price ranges. Restaurant owners need a platform to manage their listings and reach more customers. City analysts require data-driven insights to understand dining trends and support local businesses. This dashboard was created to address these needs by providing a centralized, interactive platform for restaurant data exploration and management.

**Stakeholders:**  
- Dallas residents and visitors seeking dining options  
- Restaurant owners and managers  
- City officials and business analysts  
- Data scientists and developers interested in urban analytics

**Scope & Goals:**  
- Aggregate and present restaurant data for Dallas in an accessible format  
- Enable users to search, filter, and visualize restaurants by cuisine, price, and location  
- Provide CRUD operations for restaurant management, including soft-archiving and restoration  
- Offer analytics and visualizations to reveal dining trends and patterns  
- Support future integration with LLMs for natural language queries and advanced analytics

**Measurable Outcomes:**  
- Number of restaurants managed and visualized  
- User engagement metrics (searches, CRUD actions)  
- Accuracy and freshness of restaurant data  
- Quality of analytics and insights generated

**Target Users & Use Cases:**  
- Dallas residents seeking restaurant recommendations  
- Restaurant owners managing their listings  
- City analysts tracking restaurant trends  
- Use cases: restaurant search/filter, map-based exploration, data management, analytics

**Business Problem:**  
Enable users to efficiently discover, analyze, and manage restaurant data, improving dining decisions and supporting business intelligence for local stakeholders.

---

## b. Database Design and Implementation

### Conceptual Design (ERD)

**Entities Identified:**  
- `Restaurants`: Stores core restaurant data. Fields: `restaurant_id` (PK), `name`, `street_address`, `city`, `state`, `zip_code`, `phone`, `website`, `description`, `latitude`, `longitude`, `is_active` (for soft delete).
- `CuisineTypes`: Stores cuisine categories. Fields: `cuisine_id` (PK), `cuisine_name`.
- `PriceRanges`: Stores price level symbols. Fields: `price_range_id` (PK), `price_symbol` (e.g., $, $$, $$$, $$$$), `description`.
- `RestaurantCuisines`: Many-to-many relationship between restaurants and cuisines. Fields: `restaurant_id` (FK), `cuisine_id` (FK).
- `RestaurantPricing`: Links restaurants to price ranges. Fields: `restaurant_id` (FK), `price_range_id` (FK).

**Example Table Schemas:**
```sql
CREATE TABLE Restaurants (
    restaurant_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    street_address VARCHAR(150),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    phone VARCHAR(20),
    website VARCHAR(100),
    description TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE CuisineTypes (
    cuisine_id INT PRIMARY KEY AUTO_INCREMENT,
    cuisine_name VARCHAR(50) NOT NULL
);

CREATE TABLE PriceRanges (
    price_range_id INT PRIMARY KEY AUTO_INCREMENT,
    price_symbol VARCHAR(4) NOT NULL,
    description VARCHAR(100)
);

CREATE TABLE RestaurantCuisines (
    restaurant_id INT,
    cuisine_id INT,
    PRIMARY KEY (restaurant_id, cuisine_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id),
    FOREIGN KEY (cuisine_id) REFERENCES CuisineTypes(cuisine_id)
);

CREATE TABLE RestaurantPricing (
    restaurant_id INT PRIMARY KEY,
    price_range_id INT,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id),
    FOREIGN KEY (price_range_id) REFERENCES PriceRanges(price_range_id)
);
```

**Relationships & Cardinality:**  
- A restaurant can have multiple cuisines (many-to-many via `RestaurantCuisines`).
- A restaurant has one price range (one-to-many via `RestaurantPricing`).
- Each cuisine can be associated with many restaurants.
- Each price range can be assigned to many restaurants.

**Relationships in Words:**  
- Each restaurant may offer multiple cuisines; each cuisine may be offered by multiple restaurants.
- Each restaurant is assigned a single price range.
- Restaurants can be archived/restored without data loss (using `is_active`).

**LLM-Assisted ERD Generation:**  
Prompt: "Design a normalized ERD for a restaurant dashboard with support for multiple cuisines, price ranges, and soft delete."  
Refinement: Iterated to ensure support for many-to-many cuisines, price range flexibility, and soft delete via `is_active`. LLM suggested using linking tables for many-to-many relationships and a boolean flag for soft delete.

### Logical Design

**Transformation to Tables:**  
- Each entity and relationship is mapped to a table with appropriate primary and foreign keys.
- Linking tables (`RestaurantCuisines`, `RestaurantPricing`) ensure normalization and flexibility.

**Normalization Process:**  
- 1NF: All tables have atomic columns, no repeating groups.
- 2NF: All non-key attributes fully depend on the primary key.
- 3NF: No transitive dependencies; all attributes depend only on the key.
- No denormalization; all relationships are normalized for scalability and integrity.

**Indexing Strategy:**  
- Primary keys on all tables for fast lookups.
- Foreign keys indexed for efficient joins.
- `is_active` indexed for quick filtering of active/archived restaurants.
- Composite keys in linking tables for uniqueness and performance.

**Performance Considerations:**  
- Joins are optimized by indexing foreign keys.
- Grouping and filtering operations leverage indexes for speed.
- Soft delete avoids costly deletes and preserves historical data.

---

## c. Application Architecture

### Streamlit UI Design

**Layout & Navigation:**  
- Sidebar navigation provides access to all major features: Home, Restaurant Search, Map, and Manage Restaurants. The sidebar also displays connection status and project info.
- Main content area dynamically updates based on the selected page, using Streamlit's radio and tab components for navigation and organization.
- Management functions are organized into tabs: Archive, Restore, View All, Add, and Update, allowing users to perform CRUD operations efficiently.

**User Workflow & Experience:**  
- Users begin on the Home page, which introduces the dashboard and its features.
- The Restaurant Search page allows filtering by name, price, and cuisine, with results displayed in a responsive table.
- The Map page visualizes restaurant locations using Folium, with color-coded markers for price ranges and tooltips for quick info.
- The Manage Restaurants page provides tabs for archiving/restoring restaurants (soft delete), viewing all records, adding new entries, and updating existing ones.
- Session state is used to persist filter selections, checkbox states, and form inputs, ensuring a smooth user experience across interactions.

**User Roles & Permissions:**  
- All users can search, view, and explore restaurant data.
- Admins or authorized users can add, update, archive, and restore records. (Role-based access can be added in future versions.)

**Session State Management:**  
- Streamlit's `st.session_state` is used to track filter selections, selected restaurants for archiving/restoring, and form inputs. This enables multi-step workflows and prevents data loss on reruns.

**Error Handling & Validation:**  
- All forms validate required fields before submission, displaying error messages for missing or invalid data.
- Database connection errors are caught and displayed in the sidebar.
- CRUD operations use try/except blocks to handle SQL errors and rollback transactions if needed.
- User feedback is provided via success, warning, and error messages, as well as visual cues (balloons, metrics).

**CRUD Logic Details:**  
- Create: Users fill out a form to add a new restaurant, with validation for required fields and selection of price/cuisines.
- Read: Data is fetched from the database using SQL joins, displayed in tables and maps, and filtered by user input.
- Update: Users select a restaurant to edit, modify its details, and save changes. Existing price/cuisine links are updated as needed.
- Delete (Archive/Restore): Soft delete is implemented by toggling the `is_active` flag. Archived restaurants can be restored at any time.

**Navigation Example:**
```python
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Restaurant Search", "Find Food Near Me!", "Manage Restaurants"]
)
```

**UI Customization:**  
- Custom CSS is injected to style buttons, tables, and headings, providing a modern, visually appealing interface.
- Images and icons are used to enhance the user experience and reinforce branding.

---

## d. Analytics Implementation

### Features & Methodology

**Overview:**  
The dashboard provides analytics and visualizations to help users understand restaurant distribution, pricing, cuisine trends, and geographic patterns. These insights support decision-making for diners, business owners, and city analysts.

**Visualizations:**  
- **Interactive Map (Folium):** Displays restaurant locations with color-coded markers for price ranges. Users can visually explore clusters and outliers, and access details via tooltips and popups.
- **Tabular Insights (Streamlit DataFrame):** Search results and status overviews are presented in sortable, filterable tables, allowing users to analyze restaurant attributes and trends.
- **Summary Metrics:** Key performance indicators (KPIs) such as total restaurants, active/archived counts, and cuisine diversity are displayed using Streamlit's metric components.

**Example Analytics Queries:**
- Distribution of restaurants by price range:
  ```sql
  SELECT pr.price_symbol, COUNT(*) AS count
  FROM Restaurants r
  JOIN RestaurantPricing rp ON r.restaurant_id = rp.restaurant_id
  JOIN PriceRanges pr ON rp.price_range_id = pr.price_range_id
  WHERE r.is_active = TRUE
  GROUP BY pr.price_symbol;
  ```
- Most popular cuisines:
  ```sql
  SELECT ct.cuisine_name, COUNT(*) AS count
  FROM RestaurantCuisines rc
  JOIN CuisineTypes ct ON rc.cuisine_id = ct.cuisine_id
  GROUP BY ct.cuisine_name
  ORDER BY count DESC;
  ```
- Geospatial clustering (visualized on map):
  - Restaurants are plotted by latitude/longitude, with marker color indicating price range.

**Interactive Features:**  
- Users can filter analytics by price, cuisine, and location.
- Map markers provide instant access to restaurant details.
- Data tables can be sorted and filtered for deeper analysis.

**Methodology:**  
- Data is fetched from the MySQL database using optimized SQL queries.
- Pandas is used for data manipulation, aggregation, and preparation for visualization.
- Folium and Streamlit components render interactive maps and tables.

**Sample Output:**
- A map showing clusters of budget-friendly restaurants in downtown Dallas.
- A table listing the top 5 most common cuisines.
- Metrics showing the ratio of active to archived restaurants.

---

## e. LLM Integration Strategy

**Architecture & Integration Points**

**Current Use of LLMs:**  
- LLMs (GitHub Copilot, ChatGPT, Claude) were used to assist in documentation, ERD design, SQL schema generation, and code review.
- Prompts included requests for normalized schema, ERD refinement, and best practices for CRUD and analytics implementation.

**Potential Application Integration:**  
- **SQL Chat:** Integrate an LLM (e.g., OpenAI GPT-4) to allow users to ask natural language questions about the restaurant database. The LLM translates user intent into SQL queries, validates them, and returns results in the dashboard.
- **RAG (Retrieval-Augmented Generation):** Use a vector database (e.g., ChromaDB) to store restaurant documents and enable semantic search. LLM retrieves relevant chunks and generates answers or summaries for users.

**Prompt Engineering Approach:**  
- Prompts are designed to be clear, context-rich, and goal-oriented (e.g., "Show me all Italian restaurants under $50 in downtown Dallas").
- LLM validates and sanitizes queries to prevent SQL injection and ensure safe execution.

**Security Measures:**  
- All user-generated queries are parameterized and validated before execution.
- API keys for LLM services are stored securely using environment variables or secret managers.
- Error handling includes user-friendly messages and logging for failed queries or API issues.

**Example Prompts & Responses:**
- Prompt: "List all vegan restaurants in Uptown Dallas."
  - LLM Response: SQL query generated, results displayed in table.
- Prompt: "What is the average price range for sushi restaurants?"
  - LLM Response: Aggregated analytics, shown as metrics or charts.

**API Management:**  
- API keys are never hardcoded; they are loaded from secure storage at runtime.
- Rate limiting and usage monitoring are implemented to prevent abuse.

**Error Handling Strategy:**  
- All LLM interactions are wrapped in try/except blocks.
- Errors are logged and surfaced to users with actionable feedback.

---

## f. Challenges and Learnings

### Key Technical Challenges & Solutions

**Database Design:**  
- Challenge: Designing a schema that supports flexible cuisine and price assignments, soft delete, and efficient queries.
- Solution: Used normalized tables with linking entities, indexed keys, and an `is_active` flag for soft delete.

**CRUD Operations:**  
- Challenge: Implementing robust CRUD logic with validation, error handling, and user feedback.
- Solution: Leveraged Streamlit forms, session state, and try/except blocks to ensure smooth user experience and data integrity.

**Analytics & Visualization:**  
- Challenge: Providing meaningful, interactive analytics without overwhelming users.
- Solution: Used Folium for maps, Streamlit metrics, and filterable tables to present insights clearly.

**LLM Integration:**  
- Challenge: Ensuring safe, accurate translation of user intent to SQL queries and analytics.
- Solution: Designed prompt engineering strategies, query validation, and secure API management.

**Team Collaboration:**  
- Challenge: Coordinating design decisions, code reviews, and documentation among team members.
- Solution: Used version control (Git), regular meetings, and LLMs for rapid prototyping and documentation.

### Lessons Learned
- Importance of normalization and modular design for scalability.
- Value of LLMs in accelerating development and improving documentation quality.
- Streamlit’s strengths for rapid UI prototyping and data-driven applications.
- Need for robust error handling and user feedback in interactive apps.

### Future Improvements
- Add user authentication and role-based permissions for secure CRUD operations.
- Integrate real LLM-powered SQL chat and RAG features for advanced analytics and natural language queries.
- Enhance analytics with ML models for restaurant recommendations and trend prediction.
- Improve error handling, logging, and monitoring for production readiness.
- Expand data sources to include reviews, ratings, and real-time updates.

---

## Appendix

- Screenshots of key interfaces (not included here)
- Example ERD diagram (not included here, but described above)
- Example SQL DDL (not included here, but inferred from code)
