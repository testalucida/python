SELECT sm.mv_id, sm.von, sm.bis, sm.netto, sm.nkv
from masterobjekt master 
inner join mietobjekt mobj on mobj.master_id = master.master_id 
inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id
inner join sollmiete sm on sm.mv_id = mv.mv_id 
where master.master_name = 'N_Lamm'
and sm.von < '2020-12-31'
and (sm.bis is NULL or sm.bis > '2020-01-31')
order by sm.von