#!/usr/bin/env ruby
require 'csv'
require 'optparse'
require 'mechanize'
require "nokogiri"

class TwseDescriptions

def self.handle_page(results, data)
    Nokogiri::HTML(data).xpath("//table[@class='h4']/tr").collect do |row|
        if row.at("td[2]").nil?
            next
        end
        symbol_descr = row.at("td[1]").text.strip
        isin = row.at("td[2]").text.strip
        if not isin.match /^[0-9A-Z]{12}$/
            next
        end
        description = symbol_descr.split("　", 2)[1]
        results << {"isin" => isin, "description" => description}
    end
end

def self.generate(options)
    agent = Mechanize.new
    results = []
    page = agent.get("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    data = page.body
    data.force_encoding('BIG5')
    handle_page(results, data.encode('UTF-8'))

    csv_string = CSV.generate do |csv|
        csv << ["isin", "local-description"]
        results.each do |row|
            csv << [ row["isin"], row["description"] ]
        end
    end
    puts csv_string
end

end

if __FILE__ == $0
    begin
        options = {}
        global = OptionParser.new do |opts|
        end

        TwseDescriptions.generate(options)
    rescue SystemExit => e
        raise e
    rescue Exception => e
        abort("twse_descriptions failed with error: #{e.message}, #{e.backtrace.inspect}")
    end
end
