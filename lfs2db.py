from osv import fields, osv
from datetime import datetime as dt

'''
Class for holding the data
'''
class bsm_data(osv.osv):
    _name = 'bsm.data'
    
    '''
    *124169*=Toimitusnumero
    *TCP90EU*=Tyyppitieto
    *102N32T0017297*=sarjanumero
    *351535052976123*=IMEI
    *BGS2-W 01.3010*=GSM versio
    *CT1P.01.013.0000*=FW versio
    *XTrac2.3.0BF*= GPS versio
    *32,1,A,1,1,T0* =HW versio
    *T2* =takuuaika
    
    '''
    _columns={
        'bsm_delivery_number': fields.char('Delivery number', size=64),
        'bsm_product_code': fields.char('Product code', size=64),
        'name': fields.char('BSM Serial'),
        'bsm_imei_code': fields.char('IMEI Code', size=15),
        'bsm_gsm_version': fields.char('GSM Version'),
        'bsm_fw_version': fields.char('FW Version'),
        'bsm_gps_version': fields.char('GPS Version'),
        'bsm_hw_version': fields.char('HW Version'),
        'bsm_warranty_time': fields.float('Warranty'),
        'bsm_warranty_code': fields.char('Warranty Code'),
        #'bsm_date': fields.datetime('Import date'),
        
        'bsm_used': fields.boolean('Used'),
        'bsm_prodlot_id': fields.many2one('stock.production.lot', 'Lot'),
        
    }
    
    _defaults = {
        'bsm_used': False
    }
    
bsm_data()

class prodlot_bsm(osv.osv):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'

    def write(self, cr, uid, ids, vals, context=None):
        res = super(prodlot_bsm, self).write(cr, uid, ids, vals, context=context)
        if len(ids) > 0:
            bsm_obj = self.pool.get('bsm.data')
            lot_obj = self.pool.get('stock.production.lot')

            for lot in lot_obj.browse(cr, uid, ids, context=context):
                print str(lot.bsm_ids)
                for bsm in lot.bsm_ids:
                    bsm_obj.write(cr, uid, bsm.id, {'bsm_used': True, 'bsm_prodlot_id': lot.id}, context=context)
        return True
            
    _columns = {
        'bsm_ids': fields.many2many('bsm.data', 'bsm_data_rel', 'bsm_id', 'prodlot_id', 'BSM serials')
    }

prodlot_bsm()


class stock_move_bsm(osv.osv):
    _name = 'stock.move'
    _inherit = 'stock.move'

    _columns = {
        'bsm_ids': fields.related('prodlot_id','bsm_ids', type='many2many', relation="bsm.data", string="BSM serials")
    }

stock_move_bsm()


'''
BSM file importer UI methods and data deserialization
'''
import os
import csv

class bsm_importer(osv.osv):

    LOCALFILEPATH = '/home/parallels/bsm/'
    
    _name='bsm.importer'
    #_inherit='mrp.product.produce'
    selected = ""
    
    def _get_selection(self, cr, uid, context=None):
        print 'bsm.importer._get_selection'
        obj = self.pool.get('bsm.data')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['bsm_imei_code', 'bsm_product_code'], context)
        res = [(r['bsm_product_code'], r['bsm_imei_code']) for r in res]
        return res
    
    def on_prodlot_change(self, cr, uid, ids, prodlot_id):
        print 'on_prodlot_change'
        v={}
        if prodlot_id:
            source_obj=self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id)
            v['prodlot_id']= source_obj.id
            self.selected = source_obj.id
        return {'value': v}
    
    def getSerials(self, cr, uid, ids, context=None):
        print 'getSerials()'
        # Read local file from the file system
        obj = self.pool.get('bsm.importer')
        filepath = obj.browse(cr, uid, ids, context=context)[0].filepath
        created = 0
        updated = 0
        bsmIDs = []
        try:
            if filepath == "":
                os.chdir(self.LOCALFILEPATH)
            else:
                os.chdir(filepath)
                
            for files in os.listdir("."):
                if files.endswith(".bsm"):
                    print 'opening file ' + files
                    prodlot = None
                    lot = obj.browse(cr, uid, ids, context=context)[0].prodlot_id
                    if lot:
                        prodlot = lot.id
                    #    prodlot = self.selected
                        
                    with open(files, 'rb') as csvfile:
                        hasHeader = True
                        bsm_obj = self.pool.get('bsm.data')
                        header = []
                        reader = csv.reader(csvfile, delimiter=',', quotechar='*')
                        '''
                        *124169*=Toimitusnumero
                        *TCP90EU*=Tyyppitieto
                        *102N32T0017297*=sarjanumero
                        *351535052976123*=IMEI
                        *BGS2-W 01.3010*=GSM versio
                        *CT1P.01.013.0000*=FW versio
                        *XTrac2.3.0BF*= GPS versio
                        *32,1,A,1,1,T0* =HW versio
                        *T2* =takuuaika
                        '''
                        
                        for row in reader:
                            if reader.line_num == 1 and hasHeader:
                                print 'header found'
                                header = row
                            elif len(row) >= 9:
                                # search for existing bsm
                                vals = {
                                    'bsm_delivery_number': row[0],
                                    'bsm_product_code': row[1],
                                    'name': row[2],
                                    'bsm_imei_code': row[3],
                                    'bsm_gsm_version': row[4],
                                    'bsm_fw_version': row[5],
                                    'bsm_gps_version': row[6],
                                    'bsm_hw_version': row[7],
                                    'bsm_warranty_time': float(row[8][1:]),
                                    'bsm_warranty_code': row[8],
                                    'bsm_prodlot_id': prodlot,
                                }
                                
                                existing = bsm_obj.search(cr, uid, args=[('name', '=', row[2])])
                                if len(existing) == 0:
                                    # create a new bsm
                                    
                                    newBSM = bsm_obj.create(cr, uid, vals, context=context)
                                    bsmIDs.append(newBSM)
                                    created += 1
                                else:
                                    print 'updating bsm for imei: ' + row[3]
                                    vals['bsm_used'] = False
                                    bsm_obj.write(cr, uid, existing, vals, context=context)
                                    for i in existing:
                                        bsmIDs.append(i)
                                    updated += 1
                                    
                        print 'created ' + str(created) + ' bsm rows'
                        if lot:
                            print 'Adding ids ' + str(bsmIDs) + ' to prodlot ' + str(lot.id)
                            lobj = self.pool.get('stock.production.lot')
                            #for i in bsmIDs:
                                #lobj.write(cr, uid, [lot.id], {'bsm_ids': (4, i)})
                            lobj.write(cr, uid, [lot.id], {'bsm_ids': [(6, 0, bsmIDs)]}, context=context)
                            
                        csvfile.close()
                        # rename file to mark it read
                        print 'renaming ' + filepath+files + ' to ' + filepath+files+'r'
                        #os.chmod(filepath+files, 555)
                        os.rename(filepath+files, filepath+files+'r')
                        
        except IOError as ioe:
            print "I/O error({0}): {1}".format(ioe.errno, ioe.strerror)
        except ValueError as fe:
            print fe
        except Exception as e:
            print e
        
        return self.pool.get('warning').info(cr, uid, title='BSM', message="%s BSM rows created, %s BSM rows updated"%(str(created), str(updated)))
    
    
    def addBSM(self, cr, uid, context=None):
        print 'addBSM'
        
        return {
            'view_id': 'bsm_data_view',
            'views': 'form',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'bsm.data',
            #'res_id': prod.move_created_ids2[len(prod.move_created_ids2)-1].id,
            'view_mode': 'form',
            'target': 'new',
            'context': context,
       }

    def _get_bsm_data(self, cr, uid, name, ids, context=None):
        print 'get bsm data'
        obj = self.pool.get('bsm.data')
        
    def _get_selection(self, cr, uid, context=None):
        print '_get_selection'
        obj = self.pool.get('bsm.data')
        
        unused = obj.search(cr, uid, args=[('bsm_used', '=', False)], context=context)
        
        data = obj.read(cr, uid, unused,['id', 'bsm_imei_code', 'bsm_product_code'], context=context)
        res = ()
        if len(data) > 0:
            # return list of tuples
            res = [(r['id'], r['bsm_imei_code']+','+r['bsm_product_code']) for r in data]
        return res
        
    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code'),#, selection=_get_selection)
        'imeis_name': fields.selection(_get_selection,'Unused IMEI codes'), 
        'prodlot_id' : fields.many2one('stock.production.lot', 'Lot'),
        'filepath': fields.char('BSM Filepath', required=False)
    }
    
    _defaults={
        'filepath': '/home/bsm/bsmdata/',
    }
    
bsm_importer()

