
-- Copy FDTD Subgridding rows to Subgridding table
insert into Subgridding (Title)
	select `Title` from Papers 
		where `Why_interesting` = 'Subgridding' and `Title` not in (
			select `Title` from Subgridding
		);

-- Create view.
create view Subgridding_Papers as
	select Subgridding.*, Papers.*
	from Subgridding
		left join Papers on Subgridding.Title = Papers.Title;

-- Delete view.
drop view Subgridding_Papers;

-- Another view.
create table Probe (
	`Title` text not null unique,
	primary key(Title)
);
insert into Probe (`Title`)
	select `Title` from Papers 
		where 
			`Subject_field` like '%Probe%' and 
			`Title` not in (select `Title` from Probe);
create view Probe_Papers as
	select Probe.*, Papers.*
	from Probe
		left join Papers on Probe.Title = Papers.Title;

-- Copy table.
create table Papers2 as select * from Papers;
-- Clear table.
delete from Papers;
-- Extract something.
insert into Papers select * from Papers2 where `Subject_field` = 'Tesla turbine';
insert into Papers select * from Papers2 where `Subject_field` = 'Hydrostatic transmission';
drop table Papers2;

-- Replace
update Papers
	set `Journal_Conference_Other_Source` = 'IEEE Transactions on Antennas and Propagation'
	where `Journal_Conference_Other_Source` = 'Antennas and Propagation, IEEE Transactions on';

-- Collect journals.
insert into Journals (Name)
	select distinct `Journal_Conference_Other_Source` from Papers 
		where 
			not (
				`Journal_Conference_Other_Source` like '%Conference%' or
				`Journal_Conference_Other_Source` like '%Workshop%' or
				`Journal_Conference_Other_Source` like '%Symposium%' or
				`Journal_Conference_Other_Source` like '%Colloquium%' or
				`Journal_Conference_Other_Source` like '%Forum%' or
				`Journal_Conference_Other_Source` like '%Proc.%' or
				`Journal_Conference_Other_Source` like '%Book%' or
				`Journal_Conference_Other_Source` like '%PhD%' or
				`Journal_Conference_Other_Source` like '%MSc%' or
				`Journal_Conference_Other_Source` like '%BSc%' or
				`Journal_Conference_Other_Source` like '%Article%' or
				`Journal_Conference_Other_Source` like '%Tutorial%' or
				`Journal_Conference_Other_Source` like '%Technical Report%' or
				`Journal_Conference_Other_Source` like '%Standard%' or
				`Journal_Conference_Other_Source` like '%Site%' or
				`Journal_Conference_Other_Source` like '%Source code%' or
				`Journal_Conference_Other_Source` = ''
			) and
			--`Journal_Conference_Other_Source` like '%IEEE%' and
			`Journal_Conference_Other_Source` not in (
				select `Name` from Journals
			);

-- Update count.
update Journals
	set `Count_of_papers` = (
		select count(`Index`)
			from Papers
			where `Journal_Conference_Other_Source` = Journals.`Name`
	);

-- String operations on specific cells.
update Papers 
	set `File` = replace(`File`, 'RF/Probes/', 'RF/Tools/Probes/')
	where `File` like 'RF/Probes/%';
-- Check it.
select * from Papers 
	where `File` like 'RF/Probes/%';
select * from Papers 
	where `File` like 'RF/Tools/Probes/%';


-- List columns.
PRAGMA table_info(Papers);

-- Change a columns a little bit.
create table tmp_Papers (
	`Index`	integer default 0,
	`Title`	text not null unique,
	`Subject_field`	text,
	`BibTeX_ID`	text,
	`BibTeX`	text,
	`File`	text,
	`Printed`	text,
	`Read`	text,
	`Observations_and_Conclusions`	text,
	`TODO`	text,
	`Interesting_keywords`	text,
	`Interesting_author`	text,
	`Why_interesting`	text,
	`Journal_Conference_Other_Source`	text,
	`Year`	integer,
	`Where_searched`	text,
	`Search_keywords`	text,
	`Reference_from`	text,
	`Reference_number`	text,
	`Because_it_cited`	text,
	`Other_source`	integer,
	primary key(`Title`)
);
insert into tmp_Papers
select
	`Index`,
	`Title`,
	`Subject_field`,
	`BibTeX_ID`,
	`BibTeX`,
	`File`,
	`Printed`,
	`Read`,
	`Observations_and_Conclusions`,
	`TODO`,
	`Interesting_keywords`,
	`Interesting_author`,
	`Why_interesting`,
	`Journal_Conference_Other_Source`,
	`Year`,
	`Where_searched`,
	`Search_keywords`,
	`Reference_from`,
	`Reference_number`,
	`Because_it_cited`,
	`Other_source`
from Papers;
drop table Papers;
alter table tmp_Papers rename to Papers;


-- Extract what to update.
select `Index`, `BibTeX`
	from Papers
	where
		`BibTeX_ID` in (
			"Antenna.miniaturization.survey",
			"Archimedian.spiral.EBG.metamaterial.backing"
		)
		and
		(
			`BibTeX` is NULL
			or
			`BibTeX` = ""
		);
	

-- List all possible interesting authors.
select distinct `Interesting_author`
from Papers
order by `Interesting_author`;
