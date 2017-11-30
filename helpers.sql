
-- Copy FDTD Subgridding rows to Subgridding table
insert into Subgridding (Title)
	select Title from Papers 
		where Why_interesting = "Subgridding" and Title not in (
			select Title from Subgridding
		);

-- Create view.
create view Subgridding_Papers as
	select Subgridding.*, Papers.*
	from Subgridding
		left join Papers on Subgridding.Title = Papers.Title;

-- Delete view.
drop view Subgridding_Papers;


-- Copy table.
create table Papers2 as select * from Papers;
-- Clear table.
delete from Papers;
-- Extract something.
insert into Papers select * from Papers2 where Subject_Field = "Tesla turbine";
insert into Papers select * from Papers2 where Subject_Field = "Hydrostatic transmission";
drop table Papers2;
