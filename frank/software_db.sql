SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Table structure for table `ac_softwareitem`
--

DROP TABLE IF EXISTS `ac_softwareitem`;
CREATE TABLE IF NOT EXISTS `ac_softwareitem` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `softwaretypeid` tinyint(3) unsigned NOT NULL default '0',
  `name` varchar(40) NOT NULL default '',
  `version` varchar(20) default NULL,
  `release` varchar(40) NOT NULL default '',
  `summary` varchar(40) NOT NULL default '',
  `description` varchar(40) NOT NULL default '',
  `srpm` varchar(40) NOT NULL default '',
  `contentid` int(20) unsigned default NULL,
  PRIMARY KEY  (`id`),
  KEY `softwaretypeid` (`softwaretypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=89 ;

--
-- Table structure for table `ac_softwaredepen`
--

DROP TABLE IF EXISTS `ac_softwaredepen`;
CREATE TABLE IF NOT EXISTS `ac_softwaredepen` (
  `id_software` int(10) unsigned NOT NULL default '0',
  `id_dependen` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_software`,`id_dependen`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

