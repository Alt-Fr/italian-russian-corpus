/*
Created: 04.03.2026
Modified: 21.05.2026
Model: PostgreSQL 12
Database: PostgreSQL 12
*/

-- Create tables section -------------------------------------------------

-- Table Русские_пословицы

CREATE TABLE "Русские_пословицы"
(
  "idPh_ru" Serial NOT NULL,
  "Текст_пословицыРус" Character varying(200) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Русские_пословицы" ADD CONSTRAINT "PK_Русские_пословицы" PRIMARY KEY ("idPh_ru")
;

-- Table Итальянские_пословицы

CREATE TABLE "Итальянские_пословицы"
(
  "idPh_it" Serial NOT NULL,
  "Текст_пословицыИт" Character varying(200) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Итальянские_пословицы" ADD CONSTRAINT "PK_Итальянские_пословицы" PRIMARY KEY ("idPh_it")
;

-- Table Слов_рус

CREATE TABLE "Слов_рус"
(
  "idWord_ru" Serial NOT NULL,
  "idPh_ru" Integer NOT NULL,
  "Словоформа_рус" Character varying(30) NOT NULL,
  "Лемма_рус" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Слов_рус" ADD CONSTRAINT "PK_Слов_рус" PRIMARY KEY ("idWord_ru","idPh_ru","Лемма_рус")
;

-- Table Слов_ит

CREATE TABLE "Слов_ит"
(
  "idWord_it" Serial NOT NULL,
  "Словоформа_ит" Character varying(30) NOT NULL,
  "Лемма_ит" Integer NOT NULL,
  "idPh_it" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Слов_ит" ADD CONSTRAINT "PK_Слов_ит" PRIMARY KEY ("idWord_it","idPh_it","Лемма_ит")
;

-- Table Рус_морф

CREATE TABLE "Рус_морф"
(
  "id_morf" Serial NOT NULL,
  "Часть_речиРус" Character(6) NOT NULL,
  "Рус_лемма" Character varying(30) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Рус_морф" ADD CONSTRAINT "PK_Рус_морф" PRIMARY KEY ("id_morf")
;

-- Table Ит_морф

CREATE TABLE "Ит_морф"
(
  "id_morf" Serial NOT NULL,
  "Часть_речиИт" Character(6) NOT NULL,
  "Ит_лемма" Character varying(30) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Ит_морф" ADD CONSTRAINT "PK_Ит_морф" PRIMARY KEY ("id_morf")
;

-- Table Тематика

CREATE TABLE "Тематика"
(
  "idPh_ru" Integer NOT NULL,
  "idPh_it" Integer NOT NULL,
  "Тема" Character varying(25) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "Тематика" ADD CONSTRAINT "PK_Тематика" PRIMARY KEY ("idPh_ru","idPh_it")
;

-- Create foreign keys (relationships) section -------------------------------------------------

ALTER TABLE "Слов_ит"
  ADD CONSTRAINT "Ит_пословица-слова"
    FOREIGN KEY ("idPh_it")
    REFERENCES "Итальянские_пословицы" ("idPh_it")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "Слов_рус"
  ADD CONSTRAINT "Рус_пословица-слова"
    FOREIGN KEY ("idPh_ru")
    REFERENCES "Русские_пословицы" ("idPh_ru")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "Слов_рус"
  ADD CONSTRAINT "Часть_речи-слово"
    FOREIGN KEY ("Лемма_рус")
    REFERENCES "Рус_морф" ("id_morf")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "Слов_ит"
  ADD CONSTRAINT "Часть_речи-слово"
    FOREIGN KEY ("Лемма_ит")
    REFERENCES "Ит_морф" ("id_morf")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "Тематика"
  ADD CONSTRAINT "Рус_пословица-тематика"
    FOREIGN KEY ("idPh_ru")
    REFERENCES "Русские_пословицы" ("idPh_ru")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "Тематика"
  ADD CONSTRAINT "Ит_пословица-тематика"
    FOREIGN KEY ("idPh_it")
    REFERENCES "Итальянские_пословицы" ("idPh_it")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

--ограничения уникальности пары для лемм
ALTER TABLE "Рус_морф"
  ADD CONSTRAINT unique_lem-postag_rus
	UNIQUE ("Часть_речиРус", "Рус_лемма")
;

ALTER TABLE "Ит_морф"
  ADD CONSTRAINT unique_lem-postag_rus
	UNIQUE ("Часть_речиИт", "Ит_лемма")
;