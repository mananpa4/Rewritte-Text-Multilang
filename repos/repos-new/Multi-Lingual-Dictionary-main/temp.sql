-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: jayanth
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
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
  CONSTRAINT `fk1` FOREIGN KEY (`word_id`) REFERENCES `words` (`word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `antonyms`
--

LOCK TABLES `antonyms` WRITE;
/*!40000 ALTER TABLE `antonyms` DISABLE KEYS */;
INSERT INTO `antonyms` VALUES (1,1,1,1,'darkness','The sun went down and darkness fell'),(1,2,2,2,'put-out','He crossed to the bedside table and put out the light.'),(1,3,3,3,'dark','it was a dark night.'),(2,1,1,1,'dullness','His performance was tasteful and restrained to the point of dullness.'),(2,2,2,2,'unhurried','It is an unhurried film.'),(2,3,3,3,'slow','The traffic is heavy and slow.'),(2,4,4,4,'slowly','The cars on the road are all moving slowly.'),(3,1,1,1,'regression',' This can cause regression in a pupil\'s learning process.'),(3,2,2,2,'retreat',' After her defeat, she retreated from politics.'),(3,3,3,3,'last','I last saw him in the supermarket.'),(4,1,1,0,'0','I last saw a monkey climbing on the tree.'),(5,1,1,0,' ','I last saw a monkey climbing on the tree.');
/*!40000 ALTER TABLE `antonyms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `languages1`
--

DROP TABLE IF EXISTS `languages1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `languages1` (
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
  CONSTRAINT `fk2` FOREIGN KEY (`word_id`) REFERENCES `words` (`word_id`),
  CONSTRAINT `fk6` FOREIGN KEY (`pos_id`) REFERENCES `parts_of_speech` (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf32;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `languages1`
--

LOCK TABLES `languages1` WRITE;
/*!40000 ALTER TABLE `languages1` DISABLE KEYS */;
INSERT INTO `languages1` VALUES (1,1,1,'?????','???????','?????');
/*!40000 ALTER TABLE `languages1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_of_speech`
--

DROP TABLE IF EXISTS `parts_of_speech`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_of_speech` (
  `pos_id` int NOT NULL,
  `pos_name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_of_speech`
--

LOCK TABLES `parts_of_speech` WRITE;
/*!40000 ALTER TABLE `parts_of_speech` DISABLE KEYS */;
INSERT INTO `parts_of_speech` VALUES (1,'noun'),(2,'verb'),(3,'adjective'),(4,'adverb'),(5,'pronoun');
/*!40000 ALTER TABLE `parts_of_speech` ENABLE KEYS */;
UNLOCK TABLES;

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
  `synonym_word` varchar(20) DEFAULT NULL,
  `example` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`pos_id`,`word_id`,`synonym_id`),
  KEY `fk7_idx` (`word_id`),
  CONSTRAINT `fk7` FOREIGN KEY (`word_id`) REFERENCES `words` (`word_id`),
  CONSTRAINT `fk8` FOREIGN KEY (`pos_id`) REFERENCES `parts_of_speech` (`pos_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `synonyms`
--

LOCK TABLES `synonyms` WRITE;
/*!40000 ALTER TABLE `synonyms` DISABLE KEYS */;
INSERT INTO `synonyms` VALUES (1,1,1,'glow','he town\'s lights cast a glow on the horizon.'),(2,1,1,'fasting','  I was hospitalised after three days of fasting.'),(3,1,1,'progress','The project showed slow but steady progress.'),(4,1,1,'null','He said that he had shot 13 tigers and 28 leopards.'),(5,1,1,'null','He\'s quite a cheeky little monkey.'),(1,2,2,'burn','The hot sun burned her skin.'),(2,2,2,'swift','The police took swift action against the rioters.'),(3,2,2,'proceed','We will proceed according to plan.'),(1,3,3,'bright','The lighting was too bright.'),(2,3,3,'quick','They had a quick drink at the bar.'),(3,3,3,'leading','He is a leading authority in his field.'),(2,4,4,'quickly','We\'ll repair it as quickly as possible.');
/*!40000 ALTER TABLE `synonyms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `words`
--

DROP TABLE IF EXISTS `words`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `words` (
  `word_id` int NOT NULL,
  `word_name` varchar(40) DEFAULT NULL,
  `scientific_name` varchar(50) DEFAULT NULL,
  `pronunciation` varchar(50) DEFAULT NULL,
  `images` tinyblob,
  PRIMARY KEY (`word_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `words`
--

LOCK TABLES `words` WRITE;
/*!40000 ALTER TABLE `words` DISABLE KEYS */;
INSERT INTO `words` VALUES (1,'light','elctromagnetic_radiation',' laɪt',NULL),(2,'fast','Null','fæst ',NULL),(3,'advance','Null','ədvæns',NULL),(4,'tiger','panthera_tigris','taɪgər',NULL),(5,'monkey','Cercopithecidae','mʌŋki',NULL);
/*!40000 ALTER TABLE `words` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-27 11:38:28
