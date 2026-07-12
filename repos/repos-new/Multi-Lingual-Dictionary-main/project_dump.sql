-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: jayanth
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `antonyms`
--

DROP TABLE IF EXISTS `antonyms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `antonyms` (
  `word_id` int NOT NULL,
  `pos_id` int NOT NULL,
  `synonym_id` int NOT NULL,
  `antonym_id` int NOT NULL,
  `antonym_word` varchar(40) DEFAULT NULL,
  `example` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`word_id`,`pos_id`,`synonym_id`,`antonym_id`),
  CONSTRAINT `fk1` FOREIGN KEY (`word_id`) REFERENCES `sample_words` (`word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `languages`
--

DROP TABLE IF EXISTS `languages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `languages` (
  `word_id` int NOT NULL,
  `pos_id` int NOT NULL,
  `synonym_id` int NOT NULL,
  `Hindi` varchar(150) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `Sanskrit` varchar(150) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `Telugu` varchar(150) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  PRIMARY KEY (`word_id`,`pos_id`,`synonym_id`),
  KEY `fk2` (`word_id`),
  KEY `fk3_idx` (`pos_id`),
  KEY `fk4_idx` (`synonym_id`),
  CONSTRAINT `fk2` FOREIGN KEY (`word_id`) REFERENCES `sample_words` (`word_id`),
  CONSTRAINT `fk6` FOREIGN KEY (`pos_id`) REFERENCES `pos` (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf32;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pos`
--

DROP TABLE IF EXISTS `pos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pos` (
  `pos_id` int NOT NULL,
  `pos_name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sample_words`
--

DROP TABLE IF EXISTS `sample_words`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sample_words` (
  `word_id` int NOT NULL,
  `word_name` varchar(40) DEFAULT NULL,
  `scientific_name` varchar(50) DEFAULT NULL,
  `pronunciation` varchar(50) DEFAULT NULL,
  `image` longblob,
  PRIMARY KEY (`word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `synonyms`
--

DROP TABLE IF EXISTS `synonyms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `synonyms` (
  `word_id` int NOT NULL,
  `pos_id` int NOT NULL,
  `synonym_id` int NOT NULL,
  `synonym_word` varchar(40) DEFAULT NULL,
  `example` varchar(150) DEFAULT NULL,
  `definition` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`word_id`,`pos_id`,`synonym_id`),
  KEY `fk11_idx` (`pos_id`),
  CONSTRAINT `fk10` FOREIGN KEY (`word_id`) REFERENCES `sample_words` (`word_id`),
  CONSTRAINT `fk11` FOREIGN KEY (`pos_id`) REFERENCES `pos` (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-29  1:23:04
