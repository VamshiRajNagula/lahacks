
# Use the official Docker Hub Postgres 14 alpine image
FROM postgres:14-alpine

# Set environment variables (replace 'yourpassword' with your actual password)
ENV POSTGRES_PASSWORD=myverystrongpasswordnoonecanguess
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres

# Copy the SQL script into the image
COPY init.sql /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432

# Set the default command to run when starting the container
CMD ["postgres"]