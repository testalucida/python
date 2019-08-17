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
-- Table structure for table `anlage_v`
--

DROP TABLE IF EXISTS `anlage_v`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `anlage_v` (
  `whg_id` int(4) NOT NULL,
  `veranlag_jahr` year(4) NOT NULL,
  `zeile_9_miete` int(5) NOT NULL COMMENT 'Netto-Miete',
  `zeile_13_umlagen` int(5) NOT NULL COMMENT 'Nebenkostenabschläge, saldiert mit Erstattungen/Nachzahlungen für das Vorjahr',
  `zeile_33_afa` int(5) NOT NULL,
  `zeile_33_afa_art` set('linear','degressiv') COLLATE utf8mb4_unicode_ci NOT NULL,
  `zeile_33_afa_wievorjahr` set('j','n') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'j',
  `zeile_39_rg_voll_abziehbar` int(6) DEFAULT NULL,
  `zeile_40_rg_anteil_betrag` int(6) DEFAULT NULL COMMENT 'Betrag, der anteilig abzuziehen ist',
  `zeile_40_rg_anteil_prozent` tinyint(2) DEFAULT NULL COMMENT 'Wieviel Prozent der anteilige Betrag entspricht',
  `zeile_46_auf_mieter_umlegbar` int(5) NOT NULL COMMENT 'Nebenkosten + Grundsteuer\\\\n',
  `zeile_47_verwaltungskosten` int(5) NOT NULL COMMENT 'Eigenanteil am Hausgeld ohne Rücklagen + HG-Nachzahlungen',
  PRIMARY KEY (`whg_id`,`veranlag_jahr`),
  CONSTRAINT `fk_anlage_v_1` FOREIGN KEY (`whg_id`) REFERENCES `wohnung` (`whg_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
