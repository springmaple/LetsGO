import datetime

from sql import CustomTimeZone, util
from sql.report.aging_report_customer import AgingReportCustomer
from sql.report.aging_report_doc import AgingReportDoc

_aging_data = """
<?xml version="1.0" standalone="yes"?>  
<DATAPACKET Version="2.0"><METADATA><FIELDS>
<FIELD attrname="ColumnNo" fieldtype="i4" required="true"/><FIELD attrname="ColumnType" fieldtype="string" WIDTH="1"/>
<FIELD attrname="Param1" fieldtype="i4" required="true"/><FIELD attrname="Param2" fieldtype="i4" required="true"/>
<FIELD attrname="IsLocal" fieldtype="boolean"/><FIELD attrname="HeaderScript" fieldtype="bin.hex" SUBTYPE="Text" WIDTH="1"/>
</FIELDS><PARAMS/></METADATA><ROWDATA><ROW ColumnNo="0" ColumnType="" Param1="0" Param2="0" IsLocal="FALSE"/>
<ROW ColumnNo="1" ColumnType="A" Param1="0" Param2="0" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;Current Mth&apos;&#013;end;"/>
<ROW ColumnNo="2" ColumnType="A" Param1="-1" Param2="-1" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;1 Months&apos;&#013;end;"/>
<ROW ColumnNo="3" ColumnType="A" Param1="-2" Param2="-2" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;2 Months&apos;&#013;end;"/>
<ROW ColumnNo="4" ColumnType="A" Param1="-3" Param2="-3" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;3 Months&apos;&#013;end;"/>
<ROW ColumnNo="5" ColumnType="A" Param1="-4" Param2="-4" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;4 Months&apos;&#013;end;"/>
<ROW ColumnNo="6" ColumnType="B" Param1="-999999" Param2="-5" IsLocal="FALSE" HeaderScript="ObjectPascal&#013;begin&#013;Value:= &apos;5 Month &amp; above&apos;&#013;end;"/>
</ROWDATA></DATAPACKET>
"""


def get_aging_report(sql):
    rpt_obj = sql.com.RptObjects.Find('Customer.Aging.RO')
    rpt_obj.Params.Find('ActualGroupBy').Value = 'Code;CompanyName'
    rpt_obj.Params.Find('AgingData').Value = _aging_data

    today = datetime.datetime.now(tz=CustomTimeZone())
    rpt_obj.Params.Find('AgingDate').Value = today
    rpt_obj.Params.Find('AgingOn').Value = 'I'
    rpt_obj.Params.Find('AllAgent').Value = True
    rpt_obj.Params.Find('AllArea').Value = True
    rpt_obj.Params.Find('AllCompany').Value = True
    rpt_obj.Params.Find('AllCompanyCategory').Value = True
    rpt_obj.Params.Find('AllControlAccount').Value = True
    rpt_obj.Params.Find('AllCurrency').Value = True
    rpt_obj.Params.Find('AllDocProject').Value = True
    rpt_obj.Params.Find('FilterPostDate').Value = False
    rpt_obj.Params.Find('IncludePDC').Value = False
    rpt_obj.Params.Find('IncludeZeroBalance').Value = False
    rpt_obj.Params.Find('SortBy').Value = 'Code;CompanyName'
    rpt_obj.Params.Find('DateTo').Value = today

    rpt_obj.CalculateReport()
    main_data = rpt_obj.DataSets.Find('cdsMain')
    detail_data = rpt_obj.DataSets.Find('cdsDocument')

    customers = {}
    for data in util.loop_data_sets(main_data):
        aging_rpt_cust = AgingReportCustomer(data)
        customers[aging_rpt_cust.customer_code] = aging_rpt_cust.company_name

    for data in util.loop_data_sets(detail_data):
        yield AgingReportDoc(data, customers)
