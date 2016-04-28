select    e.personid, 
 CASE CHARINDEX(' ', ValueStr, 1)
     WHEN 0 THEN concat('rx-', lower(ValueStr)) -- empty or single word
     ELSE lower(concat('rx-', SUBSTRING(ValueStr, 1, CHARINDEX(' ', ValueStr, 1) - 1))) end as rxterm

from rpt.Event e join rpt.EventCode ec on e.EventCodeId = ec.EventCodeId
where OriginalTable = 'RX' and year(e.EndDate) = 2015 

union all

select   
e.PersonID,
lower(concat('proc-',pmc.CCSMinorDescription)) as procterm

from rpt.Event e join rpt.EventCode ec 
on e.eventcodeid = ec.eventcodeid
join ccs.ProcedureCodeMap pcm on ec.CodeSet = pcm.CodeType and ec.CodeValue = pcm.CodeValue
join ccs.ProcedureMinorCategory pmc on pcm.CCSMinorCode = pmc.CCSMinorCode
where year(e.EndDate) = 2015 

union all

select   
e.PersonID,
lower(concat('diag-',dmc.CCSMinorDescription)) as diagterm

from rpt.Event e join rpt.EventCode ec 
on e.eventcodeid = ec.eventcodeid
join ccs.ICD9CodeMap dcm on ec.CodeSet = dcm.CodeType and ec.CodeValue = dcm.CodeValue
join ccs.DxMinorCategory dmc on dmc.CCSMinorCode = dcm.CCSMinorCode
where year(e.EndDate) = 2015 

union all

select   personid, lower(concat('order-', CodeValue)) as orderterm

from rpt.Event e join rpt.EventCode ec 
on e.eventcodeid = ec.eventcodeid
where year(e.EndDate) = 2015 and OriginalTable = 'OR'

union all

select  e.PersonID, lower(concat('lab-',ec.CodeValue))
from rpt.Event e join rpt.EventCode ec on e.EventCodeId = ec.EventCodeId
where OriginalTable = 'RS' and year(e.EndDate) = 2015 

