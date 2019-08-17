-- MySQL dump 10.13  Distrib 8.0.17, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: my_schema_1
-- ------------------------------------------------------
-- Server version	5.7.27-0ubuntu0.18.04.1

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
-- Table structure for table `rechnung`
--

DROP TABLE IF EXISTS `rechnung`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rechnung` (
  `rg_id` int(5) NOT NULL AUTO_INCREMENT,
  `whg_id` int(4) NOT NULL,
  `rg_nr` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `betrag` float(7,2) NOT NULL,
  `firma` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rg_datum` date DEFAULT NULL COMMENT 'Rechnung ausgestellt am',
  `bemerkung` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `verteilung_jahre` tinyint(2) DEFAULT NULL COMMENT 'Anzahl der Jahre, auf die der Rechnungsbetrag verteilt werden soll',
  `rg_bezahlt_am` date DEFAULT NULL COMMENT 'Rechnung bezahlt am',
  PRIMARY KEY (`rg_id`),
  UNIQUE KEY `rg_id_UNIQUE` (`rg_id`),
  KEY `fk_rechnung_1_idx` (`whg_id`),
  CONSTRAINT `fk_rechnung_1` FOREIGN KEY (`whg_id`) REFERENCES `wohnung` (`whg_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-08-17 11:37:55
