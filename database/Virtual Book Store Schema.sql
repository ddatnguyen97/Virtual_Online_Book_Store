CREATE TABLE "book_info" (
  "book_id" varchar PRIMARY KEY,
  "title" varchar,
  "subtitle" varchar,
  "authors" varchar,
  "publisher" varchar,
  "published_date" date,
  "print_type" varchar,
  "page_count" int,
  "language" varchar,
  "categories" varchar,
  "isbn_10" varchar,
  "isbn_13" varchar,
  "is_ebook" bool,
  "list_price_amount" float,
  "retail_price_amount" float,
  "currency" varchar,
  "text_to_speech_permission" varchar,
  "epub_available" bool,
  "pdf_available" varchar
);

CREATE TABLE "customer_info" (
  "dob" date,
  "customer_phone" varchar PRIMARY KEY,
  "city_id" varchar
);

CREATE TABLE "dim_city_province" (
  "city_id" varchar PRIMARY KEY,
  "region_id" varchar,
  "name" varchar
);

CREATE TABLE "dim_region" (
  "region_id" varchar PRIMARY KEY,
  "country_id" varchar,
  "name" varchar
);

CREATE TABLE "dim_country" (
  "country_id" varchar PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "orders_info" (
  "order_id" varchar PRIMARY KEY,
  "customer_phone" varchar,
  "book_id" varchar,
  "date_id" varchar,
  "order_quantity" int,
  "payment_type_id" varchar
);

CREATE TABLE "dim_payment_type" (
  "payment_id" varchar PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "dim_date" (
  "date_id" varchar PRIMARY KEY,
  "date" date,
  "year" int,
  "quarter" int,
  "month" int,
  "day" int
);

CREATE TABLE "order_rating" (
  "order_id" varchar PRIMARY KEY,
  "customer_phone" varchar,
  "book_id" varchar,
  "rating_value" float,
  "review_text" text,
  "rating_date_id" varchar
);

ALTER TABLE "customer_info" ADD FOREIGN KEY ("city_id") REFERENCES "dim_city_province" ("city_id");

ALTER TABLE "dim_city_province" ADD FOREIGN KEY ("region_id") REFERENCES "dim_region" ("region_id");

ALTER TABLE "dim_region" ADD FOREIGN KEY ("country_id") REFERENCES "dim_country" ("country_id");

ALTER TABLE "orders_info" ADD FOREIGN KEY ("customer_phone") REFERENCES "customer_info" ("customer_phone");

ALTER TABLE "orders_info" ADD FOREIGN KEY ("book_id") REFERENCES "book_info" ("book_id");

ALTER TABLE "orders_info" ADD FOREIGN KEY ("date_id") REFERENCES "dim_date" ("date_id");

ALTER TABLE "orders_info" ADD FOREIGN KEY ("payment_type_id") REFERENCES "dim_payment_type" ("payment_id");

ALTER TABLE "order_rating" ADD FOREIGN KEY ("order_id") REFERENCES "orders_info" ("order_id");

ALTER TABLE "order_rating" ADD FOREIGN KEY ("customer_phone") REFERENCES "customer_info" ("customer_phone");

ALTER TABLE "order_rating" ADD FOREIGN KEY ("book_id") REFERENCES "book_info" ("book_id");

ALTER TABLE "order_rating" ADD FOREIGN KEY ("rating_date_id") REFERENCES "dim_date" ("date_id");
