/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.19  Distrib 10.6.25-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: livskin_db
-- ------------------------------------------------------
-- Server version	10.6.25-MariaDB-ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `vtiger_leadstatus`
--

LOCK TABLES `vtiger_leadstatus` WRITE;
/*!40000 ALTER TABLE `vtiger_leadstatus` DISABLE KEYS */;
INSERT INTO `vtiger_leadstatus` VALUES (2,'Attempted to Contact',1,112,1,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (3,'Cold',1,113,2,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (4,'Contact in Future',1,114,3,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (5,'Contacted',1,115,4,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (6,'Hot',1,116,5,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (7,'Junk Lead',1,117,6,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (8,'Lost Lead',1,118,7,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (9,'Not Contacted',1,119,8,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (10,'Pre Qualified',1,120,9,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (11,'Qualified',1,121,10,NULL);
INSERT INTO `vtiger_leadstatus` VALUES (12,'Warm',1,122,11,NULL);
/*!40000 ALTER TABLE `vtiger_leadstatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-10 15:21:05
