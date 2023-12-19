-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: sae_r309
-- ------------------------------------------------------
-- Server version	8.0.33

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
-- Table structure for table `autorisation`
--

DROP TABLE IF EXISTS `autorisation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `autorisation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_identifiant` varchar(255) NOT NULL,
  `topic` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilisateur_topic_unique` (`utilisateur_identifiant`,`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autorisation`
--

LOCK TABLES `autorisation` WRITE;
/*!40000 ALTER TABLE `autorisation` DISABLE KEYS */;
/*!40000 ALTER TABLE `autorisation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_identifiant` varchar(255) DEFAULT NULL,
  `message_texte` text,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `Topic` varchar(255) DEFAULT NULL,
  `adresse_ip` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `utilisateur_identifiant` (`utilisateur_identifiant`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`utilisateur_identifiant`) REFERENCES `utilisateurs` (`identifiant`)
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sanctions`
--

DROP TABLE IF EXISTS `sanctions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sanctions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `identifiant` varchar(255) DEFAULT NULL,
  `adresse_ip` varchar(45) DEFAULT NULL,
  `type_sanction` enum('ban','kick') NOT NULL,
  `date_sanction` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_fin_sanction` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `identifiant` (`identifiant`),
  CONSTRAINT `sanctions_ibfk_1` FOREIGN KEY (`identifiant`) REFERENCES `utilisateurs` (`identifiant`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sanctions`
--

LOCK TABLES `sanctions` WRITE;
/*!40000 ALTER TABLE `sanctions` DISABLE KEYS */;
/*!40000 ALTER TABLE `sanctions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serveur`
--

DROP TABLE IF EXISTS `serveur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `serveur` (
  `id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(255) DEFAULT NULL,
  `mot_de_passe` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serveur`
--

LOCK TABLES `serveur` WRITE;
/*!40000 ALTER TABLE `serveur` DISABLE KEYS */;
/*!40000 ALTER TABLE `serveur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateurs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) DEFAULT NULL,
  `prenom` varchar(255) DEFAULT NULL,
  `identifiant` varchar(255) DEFAULT NULL,
  `mot_de_passe` varchar(255) DEFAULT NULL,
  `adresse_ip` varchar(15) DEFAULT NULL,
  `adresse_mail` varchar(255) DEFAULT NULL,
  `statut` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_identifiant` (`identifiant`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateurs`
--

LOCK TABLES `utilisateurs` WRITE;
/*!40000 ALTER TABLE `utilisateurs` DISABLE KEYS */;
/*!40000 ALTER TABLE `utilisateurs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-19 17:34:13
