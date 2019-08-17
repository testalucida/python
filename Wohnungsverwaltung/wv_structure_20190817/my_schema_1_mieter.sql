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
-- Table structure for table `mieter`
--

DROP TABLE IF EXISTS `mieter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mieter` (
  `mieter_id` int(4) NOT NULL,
  `whg_id` int(4) DEFAULT NULL,
  `mw_knz` char(1) COLLATE utf8_unicode_ci NOT NULL COMMENT 'Geschlechtskennzeichen: *m* ännlich oder *w*eiblich',
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `vorname` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `ausweis_id` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mailto` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mobil` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `telefon` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `strasse` varchar(60) CHARACTER SET utf8 DEFAULT NULL,
  `plz` char(5) CHARACTER SET utf8 DEFAULT NULL,
  `ort` varchar(60) CHARACTER SET utf8 DEFAULT NULL,
  `kaution` int(4) DEFAULT NULL,
  `von` date DEFAULT NULL,
  `bis` date DEFAULT NULL,
  PRIMARY KEY (`mieter_id`),
  KEY `fk_mieter_1_idx` (`whg_id`),
  CONSTRAINT `fk_mieter_1` FOREIGN KEY (`whg_id`) REFERENCES `wohnung` (`whg_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
