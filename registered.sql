-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 26, 2022 at 03:25 PM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 8.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `registered`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `roles` varchar(30) NOT NULL,
  `reg_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;


-- --------------------------------------------------------

--
-- Table structure for table `route`
--

CREATE TABLE `route` (
  `route_id` int(11) NOT NULL PRIMARY KEY,
  `users_id` int(11) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp(),
  `route` varchar(30) NOT NULL,
  `Time_of_Day` int(11) DEFAULT NULL,
  `Day_of_Week` varchar(20) DEFAULT NULL,
  `Weather_Condition` varchar(30) DEFAULT NULL,
  `Road_Type` varchar(20) DEFAULT NULL,
  `Incident` varchar(30) DEFAULT NULL,
  `Traffic_Volume` int(11) DEFAULT NULL
  CONSTRAINT FK_routeUsers FOREIGN KEY (users_id)
	REFERENCES users(id)
);

ALTER TABLE `route`
  MODIFY `route_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=100;
COMMIT;

-- --------------------------------------------------------

--
-- Table structure for table `marker`
--

CREATE TABLE `powerEmail` (
  `power_id` int(11) NOT NULL PRIMARY KEY,
  `eFormat` varchar(30) NOT NULL 
);

ALTER TABLE `route`
  MODIFY `route_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=100;
COMMIT;

-- --------------------------------------------------------

--
-- Table structure for table `traffic_data`
--

CREATE TABLE traffic_data (
  TimeStamp timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  Time_of_Day time DEFAULT NULL,
  Value_of_Time_of_Day int(11) DEFAULT NULL,
  Day_of_Week varchar(20) DEFAULT NULL,
  Weather_Condition varchar(30) DEFAULT NULL,
  Road_Name varchar(20) DEFAULT NULL,
  Road_Type varchar(20) DEFAULT NULL,
  Incident varchar(30) DEFAULT NULL,
  Traffic_Volume int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;


INSERT INTO powerEmail (eFormat) VALUES
('^[A-Za-z0-9._%+-]+@lta\.gov\.sg$');

-- defaut password for admin is "admin123"
INSERT INTO users (id, username, email, password, roles, reg_date) VALUES
(10, 'admin', 'admin@gmail.com', '-2763459319632812282', 'admin', '0000-00-00 00:00:00');